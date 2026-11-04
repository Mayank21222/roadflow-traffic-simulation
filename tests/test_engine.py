import unittest
from copy import deepcopy

from app.demo import ACTIVE_FLYOVER_SCENARIO, CAPACITY_SCENARIO, DEMO_SCENARIO, SCENARIOS
from app.engine import ScenarioError, Simulation
from app.server import run_payload


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.scenario = deepcopy(DEMO_SCENARIO)

    def test_baseline_demo_regression(self):
        results = Simulation(deepcopy(DEMO_SCENARIO)).run(80)
        self.assertEqual(results["generated"], 83)
        self.assertEqual(results["completed"], 76)
        self.assertEqual(results["active"], 7)
        self.assertEqual(results["average_travel_time"], 6.14)
        self.assertEqual(results["average_waiting_time"], 1.14)
        self.assertEqual(results["max_queue_length"], 4)

    def test_connectivity_and_routing(self):
        sim = Simulation(self.scenario)
        self.assertEqual(sim.route("west", "east"), ["west_in", "east_out"])
        self.assertIsNone(sim.route("west", "south"))

    def test_vehicle_moves_and_completes(self):
        sim = Simulation(self.scenario)
        vehicle = sim.add_vehicle("west", "east")
        self.assertIsNotNone(vehicle)
        for _ in range(20): sim.step(generate=False)
        self.assertEqual(sim.results()["completed"], 1)

    def test_signal_red_creates_wait(self):
        sim = Simulation(self.scenario)
        # West/east movement is red from ticks 4 through 7.
        sim.tick = 4
        vehicle = sim.add_vehicle("west", "east")
        for _ in range(4): sim.step(generate=False)
        self.assertGreater(sim.vehicles[vehicle].wait_time, 0)
        self.assertGreater(sim.results()["max_queue_length"], 0)

    def test_road_capacity_blocks_entry_and_produces_queue(self):
        scenario = deepcopy(self.scenario)
        scenario["roads"][1]["capacity"] = 1
        sim = Simulation(scenario)
        first = sim.add_vehicle("west", "east")
        second = sim.add_vehicle("west", "east")
        for _ in range(5): sim.step(generate=False)
        self.assertIsNotNone(first); self.assertIsNotNone(second)
        self.assertGreaterEqual(sim.results()["max_queue_length"], 1)

    def test_flyover_crossing_is_not_connected(self):
        sim = Simulation(self.scenario)
        self.assertIsNone(sim.route("fly_w", "east"))
        self.assertEqual(sim.route("fly_w", "fly_e"), ["flyover"])

    def test_metrics_are_calculated(self):
        sim = Simulation(self.scenario)
        results = sim.run(40)
        self.assertGreater(results["generated"], 0)
        self.assertIn("west_in", results["roads"])
        self.assertGreaterEqual(results["roads"]["west_in"]["utilisation"], 0)

    def test_fixed_seed_is_repeatable(self):
        first, second = Simulation(self.scenario).run(50), Simulation(self.scenario).run(50)
        self.assertEqual(first, second)

    def test_api_payload_runs_and_limits_ticks(self):
        response = run_payload({"scenario": self.scenario, "ticks": 99999})
        self.assertEqual(response["results"]["tick"], 5000)
        self.assertEqual(response["scenario"]["name"], "Synthetic Central Flyover")

    def test_invalid_network_is_rejected(self):
        scenario = deepcopy(self.scenario)
        scenario["roads"][0]["to"] = "missing"
        with self.assertRaises(ScenarioError):
            Simulation(scenario)

    def test_malformed_optional_collections_are_rejected(self):
        scenario = deepcopy(self.scenario)
        scenario["signals"] = {"not": "a list"}
        with self.assertRaises(ScenarioError):
            Simulation(scenario)
        scenario = deepcopy(self.scenario)
        scenario["demand"] = ["not an object"]
        with self.assertRaises(ScenarioError):
            Simulation(scenario)

    def test_invalid_signal_movement_is_rejected(self):
        scenario = deepcopy(self.scenario)
        scenario["signals"][0]["phases"][0]["movements"] = [["flyover", "east_out"]]
        with self.assertRaises(ScenarioError):
            Simulation(scenario)

    def test_invalid_demand_and_ticks_are_rejected(self):
        scenario = deepcopy(self.scenario)
        scenario["demand"][0]["rate"] = 1.1
        with self.assertRaises(ScenarioError):
            Simulation(scenario)
        with self.assertRaises(ValueError):
            Simulation(self.scenario).run(-1)
        with self.assertRaises(ValueError):
            run_payload([])

    def test_destination_road_is_not_counted_as_a_queue(self):
        sim = Simulation(self.scenario)
        sim.add_vehicle("fly_w", "fly_e")
        for _ in range(sim.travel_ticks("flyover")):
            sim.step(generate=False)
        self.assertEqual(sim.results()["roads"]["flyover"]["max_queue"], 0)

    def test_zero_tick_results_include_all_roads(self):
        results = Simulation(self.scenario).results()
        self.assertEqual(set(results["roads"]), {road["id"] for road in self.scenario["roads"]})
        self.assertTrue(all(row["utilisation"] == 0 for row in results["roads"].values()))

    def test_active_flyover_routes_and_separation(self):
        sim = Simulation(deepcopy(ACTIVE_FLYOVER_SCENARIO))
        self.assertEqual(sim.nodes["junction"]["x"], sim.nodes["fly_cross"]["x"])
        self.assertEqual(sim.nodes["junction"]["y"], sim.nodes["fly_cross"]["y"])
        self.assertEqual(sim.route("north", "south"), ["north_ramp_in", "flyover_w", "flyover_e", "south_ramp_out"])
        self.assertEqual(sim.route("west", "east"), ["west_in", "east_out"])
        self.assertEqual(sim.route("north", "east"), ["north_in", "east_out"])
        self.assertEqual(sim.route("west", "south"), ["west_in", "south_out"])
        self.assertFalse(any(
            {road["from"], road["to"]} == {"junction", "fly_cross"}
            for road in ACTIVE_FLYOVER_SCENARIO["roads"]
        ))
        ground_route = sim.route("west", "east")
        self.assertFalse(any(
            sim.roads[road_id].get("kind") in {"ramp", "elevated"}
            for road_id in ground_route
        ))
        flyover_route = sim.route("north", "south")
        self.assertNotIn("junction", {
            node_id
            for road_id in flyover_route
            for node_id in (sim.roads[road_id]["from"], sim.roads[road_id]["to"])
        })

    def test_active_flyover_vehicle_moves_across_elevated_crossing(self):
        sim = Simulation(deepcopy(ACTIVE_FLYOVER_SCENARIO))
        self.assertIsNotNone(sim.add_vehicle("north", "south"))
        for _ in range(20):
            sim.step(generate=False)
        results = sim.results()
        self.assertEqual(results["completed"], 1)
        for road_id in ("north_ramp_in", "flyover_w", "flyover_e", "south_ramp_out"):
            self.assertGreater(results["roads"][road_id]["utilisation"], 0)

    def test_active_flyover_ground_junction_flow(self):
        sim = Simulation(deepcopy(ACTIVE_FLYOVER_SCENARIO))
        for origin, destination in (("west", "east"), ("north", "east"), ("west", "south")):
            self.assertIsNotNone(sim.add_vehicle(origin, destination))
        for _ in range(30):
            sim.step(generate=False)
        results = sim.results()
        self.assertEqual(results["completed"], 3)
        for road_id in ("west_in", "east_out", "north_in", "south_out"):
            self.assertGreater(results["roads"][road_id]["utilisation"], 0)

    def test_capacity_comparison_uses_simulation_metrics(self):
        results = Simulation(deepcopy(CAPACITY_SCENARIO)).run(80)
        self.assertGreater(results["generated"], 0)
        self.assertGreater(results["completed"], 0)
        self.assertGreater(results["average_waiting_time"], 0)
        self.assertGreater(results["roads"]["narrow_road"]["utilisation"], results["roads"]["wide_road"]["utilisation"])
        self.assertGreater(results["roads"]["narrow_exit"]["utilisation"], results["roads"]["wide_exit"]["utilisation"])

    def test_scenario_catalog_and_deterministic_execution(self):
        self.assertEqual(
            [scenario["name"] for scenario in SCENARIOS],
            ["Synthetic Central Flyover", "Active Flyover Crossing", "Road Capacity Comparison"],
        )
        for scenario in SCENARIOS:
            first = Simulation(deepcopy(scenario)).run(80)
            second = Simulation(deepcopy(scenario)).run(80)
            self.assertEqual(first, second)

    def test_api_accepts_catalog_scenarios(self):
        for scenario in SCENARIOS:
            response = run_payload({"scenario": deepcopy(scenario), "ticks": 10})
            self.assertEqual(response["scenario"]["name"], scenario["name"])
            self.assertEqual(response["results"]["tick"], 10)


if __name__ == "__main__":
    unittest.main()
