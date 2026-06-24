"""Petri net model for the smart traffic intersection simulation."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Deque


PlaceName = str
TransitionName = str


PLACES: list[PlaceName] = [
    "Red Light",
    "Green Light",
    "Yellow Light",
    "Cars Waiting",
    "Car Passed",
    "Pedestrian Waiting",
    "Pedestrian Crossing",
]


@dataclass(frozen=True)
class TransitionRule:
    """A Petri net transition with input and output token requirements."""

    name: TransitionName
    inputs: dict[PlaceName, int]
    outputs: dict[PlaceName, int]


class PetriNet:
    """Stores the current marking and fires enabled Petri net transitions."""

    transition_rules: tuple[TransitionRule, ...] = (
        TransitionRule("Switch to Green", {"Red Light": 1}, {"Green Light": 1}),
        TransitionRule(
            "Switch to Yellow", {"Green Light": 1}, {"Yellow Light": 1}
        ),
        TransitionRule("Switch to Red", {"Yellow Light": 1}, {"Red Light": 1}),
        TransitionRule("Pedestrian Request", {}, {"Pedestrian Waiting": 1}),
        TransitionRule(
            "Start Ped Crossing",
            {"Red Light": 1, "Pedestrian Waiting": 1},
            {"Red Light": 1, "Pedestrian Crossing": 1},
        ),
        TransitionRule("End Ped Crossing", {"Pedestrian Crossing": 1}, {}),
        TransitionRule(
            "Car Passing",
            {"Green Light": 1, "Cars Waiting": 1},
            {"Green Light": 1, "Car Passed": 1},
        ),
    )

    def __init__(self) -> None:
        """Create the initial marking from the original Tkinter simulation."""
        self.marking: Counter[PlaceName] = Counter(
            {"Red Light": 1, "Cars Waiting": 3}
        )
        self.event_log: Deque[str] = deque(maxlen=100)

    def is_enabled(self, transition_name: TransitionName) -> bool:
        """Return True when all input places contain enough tokens."""
        rule = self.find_transition(transition_name)
        return all(
            self.marking[place] >= count for place, count in rule.inputs.items()
        )

    def fire(self, transition_name: TransitionName) -> bool:
        """Consume input tokens and produce output tokens for an enabled rule."""
        if not self.is_enabled(transition_name):
            return False

        rule = self.find_transition(transition_name)

        for place, count in rule.inputs.items():
            self.marking[place] -= count

        for place, count in rule.outputs.items():
            self.marking[place] += count

        self.event_log.appendleft(f"EXEC: {transition_name}")
        return True

    def find_transition(self, transition_name: TransitionName) -> TransitionRule:
        """Look up a transition rule by name."""
        for rule in self.transition_rules:
            if rule.name == transition_name:
                return rule
        raise ValueError(f"Unknown transition: {transition_name}")

    def current_light(self) -> str:
        """Return the active traffic light place."""
        for light in ("Red Light", "Yellow Light", "Green Light"):
            if self.marking[light] > 0:
                return light.replace(" Light", "")
        return "Unknown"

    def marking_as_dict(self) -> dict[PlaceName, int]:
        """Return all places with explicit zeroes for display."""
        return {place: int(self.marking[place]) for place in PLACES}
