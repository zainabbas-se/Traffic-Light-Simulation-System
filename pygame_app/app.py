"""
Pygame application loop: window, timing, and draw/update wiring.
"""

from __future__ import annotations

import sys

import pygame

from .simulation import H, TrafficSimulation, W
from .ui import draw_hud, draw_scene

MAX_RUNTIME_SEC = 60.0


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Traffic Simulation System")
    win = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    sim = TrafficSimulation()
    sim.reset()

    title_font = pygame.font.SysFont("segoeui", 32, bold=True)
    body_font = pygame.font.SysFont("segoeui", 22)
    countdown_font = pygame.font.SysFont("segoeui", 22, bold=True)

    t0_ms = pygame.time.get_ticks()

    try:
        while True:
            dt = clock.tick(60) / 1000.0
            quit_early = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_early = True
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    quit_early = True
                    break
                if event.type == pygame.VIDEORESIZE:
                    ew, eh = event.size
                    win = pygame.display.set_mode((max(W, ew), max(H, eh)), pygame.RESIZABLE)

            if quit_early:
                break

            elapsed_sec = (pygame.time.get_ticks() - t0_ms) / 1000.0
            close_remaining = max(0.0, MAX_RUNTIME_SEC - elapsed_sec)

            sim.update(dt)

            draw_scene(win, sim)
            draw_hud(win, sim, title_font, body_font, close_remaining, countdown_font)
            pygame.display.flip()

            if elapsed_sec >= MAX_RUNTIME_SEC:
                break
    finally:
        pygame.quit()

    sys.exit(0)
