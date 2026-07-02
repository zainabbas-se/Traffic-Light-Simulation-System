"""Simulation control layer that preserves the original step priorities."""

from __future__ import annotations

from dataclasses import dataclass, field
import time

from petri_net import PetriNet


AUTO_STEP_INTERVAL_SECONDS = 2.1
PEDESTRIAN_CROSSING_SECONDS = 1.8


@dataclass
class SimulationEngine:
    """Coordinates user actions and automatic simulation steps."""

    net: PetriNet = field(default_factory=PetriNet)
    cycle_index: int = 0
    is_running: bool = False
    pending_pedestrian_exit_at: float | None = None

    light_cycle: tuple[str, ...] = (
        "Switch to Green",
        "Switch to Yellow",
        "Switch to Red",
    )

    def add_car(self) -> None:
        """Add one token to Cars Waiting, matching the Tkinter Add Car button."""
        self.net.marking["Cars Waiting"] += 1
        self.net.event_log.appendleft("Car Arrived")

    def request_pedestrian(self) -> None:
        """Fire the zero-input pedestrian request transition."""
        self.net.fire("Pedestrian Request")

    def run_step(self) -> str:
        """
        Execute one simulation step with the same operational priorities.

        The original GUI prioritizes pedestrians, then cars, then the normal
        light cycle. Starting a pedestrian crossing schedules a delayed exit,
        mirroring the Tkinter animation callback without changing Petri rules.
        """
        if self.process_pending_pedestrian_exit():
            return "Pedestrian Crossing Ended"

        # Priority 1: pedestrians may start crossing only while traffic is red.
        if (
            self.net.marking["Pedestrian Waiting"] >= 1
            and self.net.marking["Red Light"] >= 1
        ):
            event = self._fire_and_log(
                "Start Ped Crossing", "Pedestrian Crossing Started"
            )
            if event != "No transition fired":
                self.pending_pedestrian_exit_at = (
                    time.time() + PEDESTRIAN_CROSSING_SECONDS
                )
            return event

        # Priority 2: vehicles pass only while the green-light token exists.
        if self.net.is_enabled("Car Passing"):
            return self._fire_and_log("Car Passing", "Car Passed")

        # Priority 3: otherwise advance the normal Red -> Green -> Yellow cycle.
        transition = self.light_cycle[self.cycle_index % len(self.light_cycle)]
        if self.net.fire(transition):
            self.cycle_index += 1
            return transition

        return "No transition fired"

    def reset(self) -> None:
        """Restore the initial marking, logs, counters, and timers."""
        self.net = PetriNet()
        self.cycle_index = 0
        self.is_running = False
        self.pending_pedestrian_exit_at = None
    def process_pending_pedestrian_exit(self) -> bool:
        """Complete a scheduled pedestrian crossing when its delay expires."""
        if self.pending_pedestrian_exit_at is None:
            return False

        if time.time() < self.pending_pedestrian_exit_at:
            return False

        self.pending_pedestrian_exit_at = None
        return (
            self._fire_and_log("End Ped Crossing", "Pedestrian Crossing Ended")
            != "No transition fired"
        )

    def _fire_and_log(self, transition: str, event: str) -> str:
        """Fire a transition and append an educational event label."""
        if self.net.fire(transition):
            self.net.event_log.appendleft(event)
            return event
        return "No transition fired"
