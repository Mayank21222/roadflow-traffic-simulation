"""Synthetic, self-contained traffic scenarios."""

DEMO_SCENARIO = {
    "name": "Synthetic Central Flyover",
    "seed": 42,
    "nodes": [
        {"id": "west", "x": 55, "y": 225}, {"id": "junction", "x": 330, "y": 225},
        {"id": "east", "x": 615, "y": 225}, {"id": "north", "x": 330, "y": 45},
        {"id": "south", "x": 330, "y": 405}, {"id": "fly_w", "x": 55, "y": 110},
        {"id": "fly_e", "x": 615, "y": 110},
    ],
    "roads": [
        {"id": "west_in", "from": "west", "to": "junction", "lanes": 1, "width": 3.2, "speed_limit": 50, "length": 80, "level": 0},
        {"id": "east_out", "from": "junction", "to": "east", "lanes": 2, "width": 6.5, "speed_limit": 50, "length": 80, "level": 0},
        {"id": "north_in", "from": "north", "to": "junction", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 60, "level": 0},
        {"id": "south_out", "from": "junction", "to": "south", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 60, "level": 0},
        {"id": "flyover", "from": "fly_w", "to": "fly_e", "lanes": 2, "width": 7, "speed_limit": 70, "length": 160, "level": 1},
    ],
    "signals": [{"node": "junction", "phase_ticks": 4, "phases": [
        {"name": "east-west green", "movements": [["west_in", "east_out"]]},
        {"name": "north-south green", "movements": [["north_in", "south_out"]]},
    ]}],
    "demand": [{"origin": "west", "destination": "east", "rate": 0.62}, {"origin": "north", "destination": "south", "rate": 0.42}],
    "synthetic": True,
}

ACTIVE_FLYOVER_SCENARIO = {
    "name": "Active Flyover Crossing",
    "description": "At-grade turning traffic shares a junction while north-south traffic uses a connected elevated flyover.",
    "seed": 42,
    "nodes": [
        {"id": "west", "x": 55, "y": 225}, {"id": "junction", "x": 330, "y": 225},
        {"id": "east", "x": 615, "y": 225}, {"id": "north", "x": 330, "y": 45},
        {"id": "south", "x": 330, "y": 405},
        {"id": "fly_w", "x": 55, "y": 110, "kind": "ramp"},
        {"id": "fly_cross", "x": 330, "y": 225, "kind": "elevated"},
        {"id": "fly_e", "x": 615, "y": 110, "kind": "ramp"},
    ],
    "roads": [
        {"id": "west_in", "from": "west", "to": "junction", "lanes": 1, "width": 3.2, "speed_limit": 50, "length": 80, "level": 0, "kind": "ground"},
        {"id": "east_out", "from": "junction", "to": "east", "lanes": 2, "width": 6.5, "speed_limit": 50, "length": 80, "level": 0, "kind": "ground"},
        {"id": "north_in", "from": "north", "to": "junction", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 60, "level": 0, "kind": "ground"},
        {"id": "south_out", "from": "junction", "to": "south", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 60, "level": 0, "kind": "ground"},
        {"id": "north_ramp_in", "from": "north", "to": "fly_w", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 40, "level": 0, "kind": "ramp"},
        {"id": "flyover_w", "from": "fly_w", "to": "fly_cross", "lanes": 2, "width": 7, "speed_limit": 70, "length": 80, "level": 1, "kind": "elevated"},
        {"id": "flyover_e", "from": "fly_cross", "to": "fly_e", "lanes": 2, "width": 7, "speed_limit": 70, "length": 80, "level": 1, "kind": "elevated"},
        {"id": "south_ramp_out", "from": "fly_e", "to": "south", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 40, "level": 0, "kind": "ramp"},
    ],
    "signals": [{"node": "junction", "phase_ticks": 4, "phases": [
        {"name": "west approach green", "movements": [["west_in", "east_out"], ["west_in", "south_out"]]},
        {"name": "north approach green", "movements": [["north_in", "east_out"]]},
    ]}],
    "demand": [
        {"origin": "west", "destination": "east", "rate": 0.55, "label": "West → East demand / tick"},
        {"origin": "north", "destination": "east", "rate": 0.25, "label": "North → East demand / tick"},
        {"origin": "west", "destination": "south", "rate": 0.20, "label": "West → South demand / tick"},
        {"origin": "north", "destination": "south", "rate": 0.45, "label": "North → South flyover demand / tick"},
    ],
    "synthetic": True,
}

CAPACITY_SCENARIO = {
    "name": "Road Capacity Comparison",
    "description": "Two parallel corridors receive the same demand rate; the narrow corridor has capacity 4/1 and the wide corridor capacity 12/6.",
    "seed": 42,
    "nodes": [
        {"id": "narrow_west", "x": 70, "y": 120}, {"id": "narrow_mid", "x": 340, "y": 120},
        {"id": "narrow_east", "x": 610, "y": 120}, {"id": "wide_west", "x": 70, "y": 330},
        {"id": "wide_mid", "x": 340, "y": 330}, {"id": "wide_east", "x": 610, "y": 330},
    ],
    "roads": [
        {"id": "narrow_road", "from": "narrow_west", "to": "narrow_mid", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 120, "capacity": 4, "level": 0, "kind": "ground"},
        {"id": "narrow_exit", "from": "narrow_mid", "to": "narrow_east", "lanes": 1, "width": 3.2, "speed_limit": 40, "length": 40, "capacity": 1, "level": 0, "kind": "ground"},
        {"id": "wide_road", "from": "wide_west", "to": "wide_mid", "lanes": 3, "width": 9.6, "speed_limit": 40, "length": 120, "capacity": 12, "level": 0, "kind": "ground"},
        {"id": "wide_exit", "from": "wide_mid", "to": "wide_east", "lanes": 3, "width": 9.6, "speed_limit": 40, "length": 40, "capacity": 6, "level": 0, "kind": "ground"},
    ],
    "signals": [],
    "demand": [
        {"origin": "narrow_west", "destination": "narrow_east", "rate": 0.95, "label": "Narrow corridor demand / tick"},
        {"origin": "wide_west", "destination": "wide_east", "rate": 0.95, "label": "Wide corridor demand / tick"},
    ],
    "synthetic": True,
}

SCENARIOS = [DEMO_SCENARIO, ACTIVE_FLYOVER_SCENARIO, CAPACITY_SCENARIO]
