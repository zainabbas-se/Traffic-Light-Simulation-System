"""Layout and styling constants for the traffic-intersection Petri net diagram."""

from __future__ import annotations

from petri_net import PetriNet

PLACE_RADIUS = 0.38
TRANS_BAR_LENGTH = 0.44
TRANS_BAR_THICK = 0.12

COLOR_PLACE_FILL = "#ffffff"
COLOR_PLACE_BORDER = "#64748b"
COLOR_TRANS_FILL = "#334155"
COLOR_TRANS_BORDER = "#334155"
COLOR_ARC = "#cbd5e1"
COLOR_HIGHLIGHT = "#0ea5e9"
COLOR_TEXT_DIM = "#475569"
COLOR_TEXT_BOLD = "#0f172a"

# Wider canvas — three separated zones, minimal overlap.
PLACE_POS: dict[str, tuple[float, float]] = {
    "Red Light": (2.4, 6.4),
    "Green Light": (6.2, 6.4),
    "Yellow Light": (10.0, 6.4),
    "Pedestrian Waiting": (2.2, 3.75),
    "Pedestrian Crossing": (2.2, 2.45),
    "Cars Waiting": (9.8, 3.6),
    "Car Passed": (9.8, 1.9),
}

TRANS_POS: dict[str, tuple[float, float]] = {
    "Switch to Green": (4.3, 6.4),
    "Switch to Yellow": (8.1, 6.4),
    "Switch to Red": (3.8, 5.1),
    "Pedestrian Request": (2.2, 4.55),
    "Start Ped Crossing": (4.2, 3.75),
    "End Ped Crossing": (2.2, 1.35),
    "Car Passing": (8.0, 4.8),
}

# v = thin vertical bar, h = thin horizontal bar (classic Petri net style).
TRANS_ORIENT: dict[str, str] = {
    "Switch to Green": "v",
    "Switch to Yellow": "v",
    "Switch to Red": "v",
    "Pedestrian Request": "h",
    "Start Ped Crossing": "v",
    "End Ped Crossing": "h",
    "Car Passing": "v",
}

PLACE_LABELS: dict[str, str] = {
    "Red Light": "Red light",
    "Green Light": "Green light",
    "Yellow Light": "Yellow light",
    "Cars Waiting": "Cars waiting",
    "Car Passed": "Car passed",
    "Pedestrian Waiting": "Ped waiting",
    "Pedestrian Crossing": "Ped crossing",
}

TRANSITION_LABELS: dict[str, str] = {
    "Switch to Green": "Turn green",
    "Switch to Yellow": "Turn yellow",
    "Switch to Red": "Turn red",
    "Pedestrian Request": "Ped button",
    "Start Ped Crossing": "Start walk",
    "End Ped Crossing": "End walk",
    "Car Passing": "Car drives",
}

# Label offset from transition center: (dx, dy, ha, va).
TRANS_LABEL_ANCHOR: dict[str, tuple[float, float, str, str]] = {
    "Switch to Green": (0, -0.38, "center", "top"),
    "Switch to Yellow": (0, -0.38, "center", "top"),
    "Switch to Red": (-0.6, 0, "right", "center"),
    "Pedestrian Request": (0.62, 0, "left", "center"),
    "Start Ped Crossing": (0, -0.38, "center", "top"),
    "End Ped Crossing": (0.62, 0, "left", "center"),
    "Car Passing": (-0.6, 0, "right", "center"),
}

TOKEN_COLOR_FOR_PLACE: dict[str, str] = {
    "Red Light": "#ef4444",
    "Green Light": "#22c55e",
    "Yellow Light": "#facc15",
    "Cars Waiting": "#3b82f6",
    "Car Passed": "#16a34a",
    "Pedestrian Waiting": "#f97316",
    "Pedestrian Crossing": "#fb923c",
}

SECTIONS: tuple[dict[str, object], ...] = (
    {
        "title": "1 · Traffic light",
        "xy": (0.4, 5.35),
        "width": 11.2,
        "height": 1.55,
        "fill": "#eff6ff",
        "edge": "#bfdbfe",
    },
    {
        "title": "2 · Pedestrians",
        "xy": (0.4, 0.35),
        "width": 5.4,
        "height": 4.75,
        "fill": "#fff7ed",
        "edge": "#fed7aa",
    },
    {
        "title": "3 · Cars",
        "xy": (6.2, 0.35),
        "width": 5.4,
        "height": 4.75,
        "fill": "#f0fdf4",
        "edge": "#bbf7d0",
    },
)

ALL_NODE_POSITIONS: dict[str, tuple[float, float]] = {
    **PLACE_POS,
    **TRANS_POS,
}


def _build_arcs() -> tuple[list[tuple[str, str]], set[tuple[str, str]]]:
    """Derive arc endpoints from `PetriNet.transition_rules`."""
    arcs: list[tuple[str, str]] = []
    dashed: set[tuple[str, str]] = set()

    for rule in PetriNet.transition_rules:
        if not rule.inputs:
            for place in rule.outputs:
                dashed.add((rule.name, place))
        for place in rule.inputs:
            arcs.append((place, rule.name))
        for place in rule.outputs:
            arcs.append((rule.name, place))

    return arcs, dashed


ARCS_DEF, DASHED_ARCS = _build_arcs()

# Gentle curves keep long arcs readable and away from other nodes.
CURVED_ARC_RAD: dict[tuple[str, str], float] = {
    ("Yellow Light", "Switch to Red"): -0.22,
    ("Switch to Red", "Red Light"): -0.18,
    ("Red Light", "Start Ped Crossing"): 0.14,
    ("Green Light", "Car Passing"): 0.12,
    ("Car Passing", "Green Light"): 0.12,
}
