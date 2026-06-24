"""
Fully automatic traffic intersection (no pygame here).

Cycle (repeats): RED 10s → YELLOW 2s → GREEN 10s → YELLOW 2s → …
- RED: pedestrians only (random spawns). Cars frozen.
- YELLOW: no movement.
- GREEN: cars only (periodic spawns). Pedestrians frozen.

Two wall-clock timers (both reset appropriately; simulation never stops):
- **Phase timer** (`time_in_phase`): 0 at each light change; counts within current colour.
- **Cycle timer** (`time_in_cycle`): 0 at the start of each full RED→…→YELLOW loop; counts within that loop.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum, auto


class LightPhase(Enum):
    RED = auto()
    GREEN = auto()
    YELLOW = auto()


# (phase, duration_seconds)
LIGHT_CYCLE: tuple[tuple[LightPhase, float], ...] = (
    (LightPhase.RED, 10.0),
    (LightPhase.YELLOW, 2.0),
    (LightPhase.GREEN, 10.0),
    (LightPhase.YELLOW, 2.0),
)

# One full loop RED → YELLOW → GREEN → YELLOW (wall seconds)
CYCLE_TOTAL_SEC: float = sum(d for _, d in LIGHT_CYCLE)

W = 1100
H = 640
ROAD_TOP = 255
ROAD_BOTTOM = 385
CAR_LANE_Y = (ROAD_TOP + ROAD_BOTTOM) // 2
CROSSWALK_X0 = 470
CROSSWALK_X1 = 630
CROSSWALK_CAR_X0 = CROSSWALK_X0 - 55
CROSSWALK_CAR_X1 = CROSSWALK_X1 + 55
PED_START_Y = 560
PED_END_Y = 215
STOP_LINE = 395
INTERSECTION_END = 705
# Scene bounds: same rules for pruning, HUD counts, and sprites (lists stay authoritative).
CAR_SCENE_X_MARGIN = 50
CAR_DESPAWN_X = INTERSECTION_END + 78
PED_SCENE_Y_MIN = ROAD_TOP - 36
PED_SCENE_Y_MAX = PED_START_Y + 30
CAR_SPACING = 76
CAR_SPEED = 220.0
PED_SPEED = 100.0

# Automatic spawns
CAR_SPAWN_INTERVAL = 3.4
PED_SPAWN_CHANCE_PER_SEC = 0.42
MAX_PEDS_ON_CROSS = 5


@dataclass
class Car:
    x: float
    prev_x: float


@dataclass
class Pedestrian:
    y: float
    x: float


@dataclass
class TrafficSimulation:
    cycle_index: int = 0
    # Phase timer: resets to 0 on every phase transition.
    time_in_phase: float = 0.0
    # Cycle timer: resets to 0 when a full RED→YELLOW→GREEN→YELLOW loop completes.
    time_in_cycle: float = 0.0
    # Increments each time we return to RED after the second YELLOW (cycle 1 = initial).
    cycle_number: int = 1

    cars: list[Car] = field(default_factory=list)
    pedestrians: list[Pedestrian] = field(default_factory=list)
    car_queue: int = 0
    _spawn_car_accum: float = 0.0

    @property
    def phase(self) -> LightPhase:
        return LIGHT_CYCLE[self.cycle_index][0]

    def phase_duration(self) -> float:
        return LIGHT_CYCLE[self.cycle_index][1]

    @property
    def current_light(self) -> str:
        return self.phase.name

    @property
    def time_left_in_phase(self) -> float:
        return max(0.0, self.phase_duration() - self.time_in_phase)

    @property
    def time_left_in_cycle(self) -> float:
        return max(0.0, CYCLE_TOTAL_SEC - self.time_in_cycle)

    def reset(self) -> None:
        self.cycle_index = 0
        self.time_in_phase = 0.0
        self.time_in_cycle = 0.0
        self.cycle_number = 1
        self._spawn_car_accum = 0.0
        self.cars.clear()
        self.pedestrians.clear()
        for i in range(3):
            x0 = float(85 + i * CAR_SPACING)
            self.cars.append(Car(x=x0, prev_x=x0))
        self.car_queue = 0

    def _cars_in_intersection(self) -> bool:
        return any(STOP_LINE <= c.x <= INTERSECTION_END for c in self.cars)

    def _car_blocks_crosswalk(self) -> bool:
        return any(CROSSWALK_CAR_X0 <= c.x <= CROSSWALK_CAR_X1 for c in self.cars)

    def _peds_in_crosswalk(self) -> bool:
        return any(PED_END_Y - 30 <= p.y <= PED_START_Y + 25 for p in self.pedestrians)

    def _advance_cycle(self) -> None:
        n = len(LIGHT_CYCLE)
        old_index = self.cycle_index
        self.cycle_index = (self.cycle_index + 1) % n
        self.time_in_phase = 0.0
        if old_index == n - 1 and self.cycle_index == 0:
            self.cycle_number += 1
            self.time_in_cycle = 0.0

    def status_headline(self) -> str:
        if self.phase is LightPhase.YELLOW:
            return "WAITING"
        if self.phase is LightPhase.GREEN:
            return "CARS MOVING"
        return "PEDESTRIANS CROSSING"

    def status_detail(self) -> str:
        return (
            f"Phase {self.cycle_index + 1}/{len(LIGHT_CYCLE)} · "
            f"Cars: {self.active_cars_on_road()} · Peds: {self.active_pedestrians_in_scene()} · "
            f"Queue: {self.car_queue}"
        )

    def active_cars_on_road(self) -> int:
        """Cars still in the active road segment (same predicate as `_car_in_scene`)."""
        return sum(1 for c in self.cars if self._car_in_scene(c))

    def active_pedestrians_in_scene(self) -> int:
        """Pedestrians still on approach / crosswalk (same predicate as `_pedestrian_in_scene`)."""
        return sum(1 for p in self.pedestrians if self._pedestrian_in_scene(p))

    @staticmethod
    def _car_in_scene(c: Car) -> bool:
        return -CAR_SCENE_X_MARGIN <= c.x <= CAR_DESPAWN_X

    @staticmethod
    def _pedestrian_in_scene(p: Pedestrian) -> bool:
        return PED_SCENE_Y_MIN <= p.y <= PED_SCENE_Y_MAX

    def update(self, dt_wall: float) -> None:
        """Always advances (fully automatic)."""
        self._tick(dt_wall)

    def _tick(self, dt_wall: float) -> None:
        self.time_in_phase += dt_wall
        self.time_in_cycle += dt_wall

        move_cars = self.phase is LightPhase.GREEN and not self._peds_in_crosswalk()
        move_peds = self.phase is LightPhase.RED and not self._car_blocks_crosswalk()

        if self.phase is LightPhase.GREEN:
            self._auto_spawn_cars(dt_wall)

        cars_moved = False
        if move_peds:
            self._update_pedestrians(dt_wall)
        elif move_cars:
            self._update_cars(dt_wall)
            cars_moved = True
        if not cars_moved:
            for c in self.cars:
                c.prev_x = c.x

        self._try_advance_phase()
        self._prune_off_scene_entities()

    def _auto_spawn_cars(self, dt: float) -> None:
        """During GREEN, add cars from queue or spawn new backlog periodically."""
        self._spawn_car_accum += dt
        while self._spawn_car_accum >= CAR_SPAWN_INTERVAL:
            self._spawn_car_accum -= CAR_SPAWN_INTERVAL
            self.car_queue += 1

        while self.car_queue > 0:
            if not self.cars:
                self.cars.append(Car(x=75.0, prev_x=75.0))
                self.car_queue -= 1
                continue
            tail = min(c.x for c in self.cars)
            if tail > 145:
                xn = float(tail - CAR_SPACING)
                self.cars.insert(0, Car(x=xn, prev_x=xn))
                self.car_queue -= 1
            else:
                break

    def _update_pedestrians(self, dt: float) -> None:
        on_cross = sum(1 for p in self.pedestrians if PED_END_Y - 45 <= p.y <= PED_START_Y + 25)
        if on_cross < MAX_PEDS_ON_CROSS and random.random() < PED_SPAWN_CHANCE_PER_SEC * dt:
            lane_slots = (-40, -14, 14, 40)
            slot = random.choice(lane_slots)
            cx = (CROSSWALK_X0 + CROSSWALK_X1) / 2 + slot
            self.pedestrians.append(Pedestrian(y=float(PED_START_Y), x=float(cx)))

        for p in self.pedestrians:
            p.y -= PED_SPEED * dt

    def _update_cars(self, dt: float) -> None:
        self.cars.sort(key=lambda c: c.x)
        n = len(self.cars)
        for i, c in enumerate(self.cars):
            old_x = c.x
            if i == n - 1:
                v = CAR_SPEED
            else:
                ahead = self.cars[i + 1]
                gap = ahead.x - c.x
                v = 0.0 if gap < CAR_SPACING else CAR_SPEED
            c.x += v * dt
            c.prev_x = old_x

    def _prune_off_scene_entities(self) -> None:
        """Each frame: lists == what is simulated and drawn; HUD uses `active_*` / len after prune."""
        self.cars = [c for c in self.cars if self._car_in_scene(c)]
        self.pedestrians = [p for p in self.pedestrians if self._pedestrian_in_scene(p)]

    def _try_advance_phase(self) -> None:
        dur = self.phase_duration()
        if self.time_in_phase < dur:
            return

        ph = self.phase
        if ph is LightPhase.GREEN:
            if self._cars_in_intersection() or self._car_blocks_crosswalk():
                self.time_in_phase = dur
                return
        elif ph is LightPhase.RED:
            if self._peds_in_crosswalk():
                self.time_in_phase = dur
                return

        self._advance_cycle()
