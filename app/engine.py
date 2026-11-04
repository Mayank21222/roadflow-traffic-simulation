"""Deterministic, discrete-time agent traffic simulation engine.

The model intentionally treats a road as a single aggregate lane group: it has a
finite occupancy, a travel time and an exit queue.  It does not model individual
lanes or lane changes.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import Any


@dataclass
class Vehicle:
    id: int
    route: list[str]
    road_index: int
    progress: int
    entered_at: int
    wait_time: int = 0
    completed_at: int | None = None

    @property
    def road_id(self) -> str:
        return self.route[self.road_index]


class ScenarioError(ValueError):
    """Raised when a scenario cannot be safely simulated."""


class Simulation:
    """Runs one mutable simulation instance from a JSON-compatible scenario."""

    def __init__(self, scenario: dict[str, Any]):
        self._validate_scenario(scenario)
        self.scenario = scenario
        self.roads = {road["id"]: road for road in scenario["roads"]}
        self.nodes = {node["id"]: node for node in scenario["nodes"]}
        self.outgoing: dict[str, list[str]] = defaultdict(list)
        for road in scenario["roads"]:
            self.outgoing[road["from"]].append(road["id"])
        self.signals = {signal["node"]: signal for signal in scenario.get("signals", [])}
        self.tick = 0
        self.rng = Random(scenario.get("seed", 1))
        self.vehicles: dict[int, Vehicle] = {}
        self.on_road: dict[str, set[int]] = defaultdict(set)
        self.next_vehicle_id = 1
        self.generated = 0
        self.completed: list[Vehicle] = []
        self.utilisation_samples: dict[str, list[float]] = defaultdict(list)
        self.max_queue: dict[str, int] = defaultdict(int)

    @staticmethod
    def _validate_scenario(scenario: dict[str, Any]) -> None:
        """Reject malformed networks rather than producing misleading results."""
        if not isinstance(scenario, dict):
            raise ScenarioError("scenario must be an object")
        nodes = scenario.get("nodes")
        roads = scenario.get("roads")
        signals = scenario.get("signals", [])
        demand_entries = scenario.get("demand", [])
        if not isinstance(nodes, list) or not isinstance(roads, list):
            raise ScenarioError("scenario requires nodes and roads arrays")
        if not isinstance(signals, list) or not isinstance(demand_entries, list):
            raise ScenarioError("signals and demand must be arrays")
        seed = scenario.get("seed", 1)
        if seed is None or not isinstance(seed, (int, float, str)):
            raise ScenarioError("seed must be a number or string")
        node_ids = [node.get("id") for node in nodes if isinstance(node, dict)]
        road_ids = [road.get("id") for road in roads if isinstance(road, dict)]
        if (len(node_ids) != len(nodes) or any(not isinstance(node_id, str) or not node_id for node_id in node_ids)
                or len(set(node_ids)) != len(node_ids)):
            raise ScenarioError("node ids must be unique non-empty values")
        if (len(road_ids) != len(roads) or any(not isinstance(road_id, str) or not road_id for road_id in road_ids)
                or len(set(road_ids)) != len(road_ids)):
            raise ScenarioError("road ids must be unique non-empty values")
        for road in roads:
            if road.get("from") not in node_ids or road.get("to") not in node_ids:
                raise ScenarioError(f"road {road.get('id')} references an unknown node")
            try:
                lanes_value = road["lanes"]
                lanes = int(lanes_value)
                if float(lanes_value) != lanes:
                    raise ValueError("lanes must be an integer")
                length, speed = float(road["length"]), float(road["speed_limit"])
                capacity_value = road.get("capacity", lanes * 6)
                capacity = int(capacity_value)
                if float(capacity_value) != capacity:
                    raise ValueError("capacity must be an integer")
                width = float(road.get("width", 1))
            except (KeyError, TypeError, ValueError) as exc:
                raise ScenarioError(f"road {road.get('id')} has invalid dimensions") from exc
            if lanes < 1 or length <= 0 or speed <= 0 or capacity < 1 or width <= 0:
                raise ScenarioError(f"road {road.get('id')} needs positive lanes, width, length, speed and capacity")
        road_by_id = {road["id"]: road for road in roads}
        for signal in signals:
            if not isinstance(signal, dict):
                raise ScenarioError("signals must be objects")
            if signal.get("node") not in node_ids or not signal.get("phases"):
                raise ScenarioError("signal needs a known node and at least one phase")
            if not isinstance(signal.get("phase_ticks"), int) or signal["phase_ticks"] < 1:
                raise ScenarioError("signal phase_ticks must be a positive integer")
            for phase in signal["phases"]:
                if not isinstance(phase, dict):
                    raise ScenarioError("signal phases must be objects")
                movements = phase.get("movements", [])
                if not isinstance(movements, list):
                    raise ScenarioError("signal phase movements must be an array")
                for movement in movements:
                    if not isinstance(movement, list) or len(movement) != 2:
                        raise ScenarioError("a signal movement must be [incoming_road, outgoing_road]")
                    incoming, outgoing = movement
                    if incoming not in road_by_id or outgoing not in road_by_id:
                        raise ScenarioError("signal movement references an unknown road")
                    if road_by_id[incoming]["to"] != signal["node"] or road_by_id[outgoing]["from"] != signal["node"]:
                        raise ScenarioError("signal movement roads must meet at its node")
        for demand in demand_entries:
            if not isinstance(demand, dict):
                raise ScenarioError("demand entries must be objects")
            if demand.get("origin") not in node_ids or demand.get("destination") not in node_ids:
                raise ScenarioError("demand references an unknown node")
            try:
                rate = float(demand["rate"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ScenarioError("demand rate must be a number from 0 to 1") from exc
            if not 0 <= rate <= 1:
                raise ScenarioError("demand rate must be from 0 to 1")

    def road_capacity(self, road_id: str) -> int:
        road = self.roads[road_id]
        if "capacity" in road:
            return int(road["capacity"])
        return int(road["lanes"]) * 6

    def travel_ticks(self, road_id: str) -> int:
        road = self.roads[road_id]
        return max(1, ceil(float(road["length"]) / float(road["speed_limit"])))

    def route(self, origin: str, destination: str) -> list[str] | None:
        """Return a shortest (fewest-road) route; grade crossings add no edges."""
        if origin == destination:
            return []
        frontier = deque([(origin, [], None)])
        visited = {(origin, None)}
        while frontier:
            node, path, incoming = frontier.popleft()
            for road_id in self.outgoing[node]:
                # A signal's movement list is also the allowed-turn definition.
                if incoming is not None and not self._movement_exists(incoming, road_id):
                    continue
                road = self.roads[road_id]
                candidate = path + [road_id]
                if road["to"] == destination:
                    return candidate
                state = (road["to"], road_id)
                if state not in visited:
                    visited.add(state)
                    frontier.append((road["to"], candidate, road_id))
        return None

    def _movement_exists(self, incoming: str, outgoing: str) -> bool:
        """Whether the movement is structurally permitted, independent of phase."""
        signal = self.signals.get(self.roads[incoming]["to"])
        if not signal:
            return True
        return any([incoming, outgoing] in phase["movements"] for phase in signal["phases"])

    def _signal_allows(self, incoming: str, outgoing: str) -> bool:
        node = self.roads[incoming]["to"]
        signal = self.signals.get(node)
        if not signal:
            return True
        phase = (self.tick // signal["phase_ticks"]) % len(signal["phases"])
        return [incoming, outgoing] in signal["phases"][phase]["movements"]

    def add_vehicle(self, origin: str, destination: str) -> int | None:
        route = self.route(origin, destination)
        if not route or len(self.on_road[route[0]]) >= self.road_capacity(route[0]):
            return None
        vehicle = Vehicle(self.next_vehicle_id, route, 0, 0, self.tick)
        self.vehicles[vehicle.id] = vehicle
        self.on_road[route[0]].add(vehicle.id)
        self.next_vehicle_id += 1
        self.generated += 1
        return vehicle.id

    def _generate_demand(self) -> None:
        for demand in self.scenario.get("demand", []):
            # probability per tick: reproducible with the scenario's fixed seed
            if self.rng.random() < float(demand["rate"]):
                self.add_vehicle(demand["origin"], demand["destination"])

    def step(self, generate: bool = True) -> None:
        if generate:
            self._generate_demand()
        # Snapshot lets every vehicle make exactly one aggregate movement decision.
        for vehicle_id in list(self.vehicles):
            vehicle = self.vehicles.get(vehicle_id)
            if vehicle is None:
                continue
            current = vehicle.road_id
            if vehicle.progress < self.travel_ticks(current):
                vehicle.progress += 1
                continue
            if vehicle.road_index == len(vehicle.route) - 1:
                self.on_road[current].remove(vehicle.id)
                vehicle.completed_at = self.tick
                self.completed.append(vehicle)
                del self.vehicles[vehicle.id]
                continue
            next_road = vehicle.route[vehicle.road_index + 1]
            has_space = len(self.on_road[next_road]) < self.road_capacity(next_road)
            if self._signal_allows(current, next_road) and has_space:
                self.on_road[current].remove(vehicle.id)
                self.on_road[next_road].add(vehicle.id)
                vehicle.road_index += 1
                vehicle.progress = 0
            else:
                vehicle.wait_time += 1
        for road_id in self.roads:
            occupancy = len(self.on_road[road_id])
            self.utilisation_samples[road_id].append(occupancy / self.road_capacity(road_id))
            waiting = sum(
                1 for v in self.vehicles.values()
                if v.road_id == road_id
                and v.road_index < len(v.route) - 1
                and v.progress >= self.travel_ticks(road_id)
            )
            self.max_queue[road_id] = max(self.max_queue[road_id], waiting)
        self.tick += 1

    def run(self, ticks: int) -> dict[str, Any]:
        if not isinstance(ticks, int) or ticks < 0:
            raise ValueError("ticks must be a non-negative integer")
        for _ in range(ticks):
            self.step()
        return self.results()

    def results(self) -> dict[str, Any]:
        travel = [v.completed_at - v.entered_at for v in self.completed if v.completed_at is not None]
        wait = [v.wait_time for v in self.completed]
        roads = {
            road_id: {
                "utilisation": round(sum(samples) / len(samples), 3) if samples else 0,
                "max_queue": self.max_queue[road_id],
                "occupancy": len(self.on_road[road_id]),
            }
            for road_id in self.roads
            for samples in [self.utilisation_samples[road_id]]
        }
        return {
            "tick": self.tick,
            "generated": self.generated,
            "completed": len(self.completed),
            "active": len(self.vehicles),
            "average_travel_time": round(sum(travel) / len(travel), 2) if travel else 0,
            "average_waiting_time": round(sum(wait) / len(wait), 2) if wait else 0,
            "max_queue_length": max(self.max_queue.values(), default=0),
            "roads": roads,
        }
