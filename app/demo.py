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
