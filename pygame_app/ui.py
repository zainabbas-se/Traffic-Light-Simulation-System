"""
Pygame rendering: real-world intersection view (no graph / Petri diagram).
"""

from __future__ import annotations

import math

import pygame

from simulation import (
    CAR_LANE_Y,
    CROSSWALK_X0,
    CROSSWALK_X1,
    H,
    INTERSECTION_END,
    LightPhase,
    PED_END_Y,
    PED_START_Y,
    ROAD_BOTTOM,
    ROAD_TOP,
    STOP_LINE,
    TrafficSimulation,
    W,
)

# Emoji 🚗 often faces left in fonts; flip so +x motion matches "front to the right".
_CAR_TEX_BASE: pygame.Surface | None = None
_CAR_TEX_EASTBOUND: pygame.Surface | None = None
_CAR_TEX_QUEUE: pygame.Surface | None = None


def _car_textures() -> tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
    global _CAR_TEX_BASE, _CAR_TEX_EASTBOUND, _CAR_TEX_QUEUE
    if _CAR_TEX_BASE is None:
        _CAR_TEX_BASE = _emoji_font(46).render("🚗", True, (0, 0, 0))
        _CAR_TEX_EASTBOUND = pygame.transform.flip(_CAR_TEX_BASE, True, False)
        _CAR_TEX_QUEUE = pygame.transform.flip(_emoji_font(22).render("🚗", True, (30, 30, 30)), True, False)
    return _CAR_TEX_BASE, _CAR_TEX_EASTBOUND, _CAR_TEX_QUEUE


def _car_sprite_for_velocity(dx: float) -> pygame.Surface:
    """Horizontal mirror only: eastbound (+x or stopped) vs westbound (-x)."""
    _base, east, _q = _car_textures()
    if dx >= -0.05:
        return east
    return _base


def _emoji_font(size: int) -> pygame.font.Font:
    for name in ("Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Arial"):
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.SysFont("arial", size)


def draw_scene(surf: pygame.Surface, sim: TrafficSimulation) -> None:
    # Road canvas height H; extend grass if the window is wider than the simulation.
    sw = surf.get_width()
    surf.fill((214, 232, 210), (0, 0, sw, H))

    # Horizontal road
    pygame.draw.rect(surf, (70, 74, 82), (0, ROAD_TOP, W, ROAD_BOTTOM - ROAD_TOP), border_radius=4)
    pygame.draw.rect(surf, (95, 99, 110), (0, CAR_LANE_Y - 3, W, 6))

    # Vertical crosswalk band
    cw = pygame.Rect(CROSSWALK_X0, ROAD_TOP - 40, CROSSWALK_X1 - CROSSWALK_X0, (ROAD_BOTTOM - ROAD_TOP) + 80)
    pygame.draw.rect(surf, (210, 210, 210), cw, border_radius=2)
    stripe_w = 10
    x = cw.x + 8
    while x < cw.right - 8:
        pygame.draw.rect(surf, (245, 245, 245), (x, cw.y + 6, stripe_w, cw.h - 12))
        x += stripe_w + 10

    # Stop line (cars hold here on red/yellow)
    pygame.draw.line(surf, (250, 250, 250), (STOP_LINE, ROAD_TOP + 6), (STOP_LINE, ROAD_BOTTOM - 6), 5)

    # Intersection outline (subtle)
    pygame.draw.rect(surf, (255, 214, 120), (STOP_LINE, ROAD_TOP, INTERSECTION_END - STOP_LINE, ROAD_BOTTOM - ROAD_TOP), 3)

    # Traffic light pole + lamps
    pole_x = int((CROSSWALK_X0 + CROSSWALK_X1) / 2 + 120)
    pole_top = ROAD_TOP - 120
    pygame.draw.line(surf, (40, 40, 45), (pole_x, pole_top), (pole_x, ROAD_TOP - 10), 6)
    box = pygame.Rect(pole_x - 34, pole_top - 10, 68, 92)
    pygame.draw.rect(surf, (34, 36, 40), box, border_radius=10)
    pygame.draw.rect(surf, (18, 20, 24), box, 2, border_radius=10)

    def lamp(y: int, color_on: tuple[int, int, int], color_dim: tuple[int, int, int], active: bool) -> None:
        c = color_on if active else color_dim
        pygame.draw.circle(surf, c, (pole_x, y), 14)
        pygame.draw.circle(surf, (10, 10, 12), (pole_x, y), 14, 2)

    y0 = box.y + 18
    lamp(y0, (255, 70, 70), (80, 30, 30), sim.phase is LightPhase.RED)
    lamp(y0 + 28, (255, 220, 60), (90, 80, 30), sim.phase is LightPhase.YELLOW)
    lamp(y0 + 56, (60, 220, 120), (25, 80, 45), sim.phase is LightPhase.GREEN)

    # Cars + peds (car sprite flips horizontally with travel direction)
    ped_font = _emoji_font(44)
    ped_tex = ped_font.render("🚶", True, (0, 0, 0))
    for c in sim.cars:
        dx = c.x - c.prev_x
        car_tex = _car_sprite_for_velocity(dx)
        surf.blit(car_tex, (int(c.x - car_tex.get_width() / 2), int(CAR_LANE_Y - car_tex.get_height() / 2)))
    for p in sim.pedestrians:
        surf.blit(ped_tex, (int(p.x - ped_tex.get_width() / 2), int(p.y - ped_tex.get_height() / 2)))

    # Queue chips (waiting cars not yet released)
    qx = 52
    qy = CAR_LANE_Y + 46
    _, _, qtex = _car_textures()
    for i in range(min(sim.car_queue, 10)):
        surf.blit(qtex, (qx + (i % 5) * 26, qy + (i // 5) * 22))
    if sim.car_queue > 10:
        tag = pygame.font.SysFont("segoeui", 18).render(f"+{sim.car_queue - 10}", True, (20, 20, 20))
        surf.blit(tag, (qx + 5 * 26 + 6, qy))


def _blit_text_shadow(
    surf: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    fg: tuple[int, int, int],
    pos: tuple[int, int],
) -> None:
    """Dark offset copy so text reads on light grass (transparent header, no white bar)."""
    x, y = pos
    shadow_rgb = (16, 26, 20)
    surf.blit(font.render(text, True, shadow_rgb), (x + 1, y + 1))
    surf.blit(font.render(text, True, fg), (x, y))


def _signal_pill_style(phase: LightPhase) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Background and foreground for the signal pill."""
    if phase is LightPhase.RED:
        return (220, 38, 38), (255, 255, 255)
    if phase is LightPhase.GREEN:
        return (22, 163, 74), (255, 255, 255)
    return (234, 179, 8), (30, 27, 15)


def draw_hud(
    surf: pygame.Surface,
    sim: TrafficSimulation,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    window_close_remaining_sec: float,
    countdown_font: pygame.font.Font,
) -> None:
    pad_x = 28
    pad_y = 18
    gap = 14

    # No opaque header strip — grass from draw_scene shows through (transparent header area).
    x = pad_x
    y = pad_y

    rem = max(0.0, float(window_close_remaining_sec))
    sec_left = 0 if rem <= 0 else max(0, int(math.ceil(rem - 1e-9)))
    close_muted = (100, 116, 139) if sec_left > 10 else (185, 28, 28)
    close_line = f"Window will close in: {sec_left} seconds"
    _blit_text_shadow(surf, countdown_font, close_line, close_muted, (x, y))
    _, close_h = countdown_font.size(close_line)
    y += close_h + gap + 2

    # Signal pill + main headline
    pill_font = pygame.font.SysFont("segoeui", 14, bold=True)
    sig = sim.current_light
    pill_bg, pill_fg = _signal_pill_style(sim.phase)
    pill_txt = pill_font.render(sig, True, pill_fg)
    pw, ph = pill_txt.get_size()
    pill_w = max(52, pw + 22)
    pill_h = 32
    pill_rect = pygame.Rect(x, y + 2, pill_w, pill_h)
    pygame.draw.rect(surf, pill_bg, pill_rect, border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255), pill_rect, 1, border_radius=10)
    surf.blit(pill_txt, (pill_rect.centerx - pw // 2, pill_rect.centery - ph // 2))

    hx = x + pill_w + 12
    headline = sim.status_headline()
    _blit_text_shadow(surf, title_font, headline, (15, 23, 42), (hx, y))
    _, head_h = title_font.size(headline)
    y += max(head_h, pill_h) + gap

    phase_left = sim.time_left_in_phase
    stats_text = (
        f"Time left in this phase: {phase_left:.1f}s   ·   Cars: {sim.active_cars_on_road()}   ·   "
        f"Pedestrians: {sim.active_pedestrians_in_scene()}"
    )
    # Phase details: larger font (main) + solid near-black for contrast (no shadow blur).
    stats_fg = (14, 16, 20)
    surf.blit(body_font.render(stats_text, True, stats_fg), (x, y))
