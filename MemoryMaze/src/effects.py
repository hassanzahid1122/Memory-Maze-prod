"""Lightweight visual-effect helpers: gradients, glow, starfield, easing.

Everything here is pure pygame drawing with no external assets, kept cheap
enough to run every frame at 60 FPS.
"""

import math
import random

import pygame

from . import config


# --------------------------------------------------------------------------- #
# Geometry / easing
# --------------------------------------------------------------------------- #
class Viewport:
    """Maps maze cells to on-screen pixels, auto-scaled to fit and centered.

    Given the maze dimensions and the rectangular screen area available for the
    play field, it picks the largest square cell size that fits and centers the
    grid, so every difficulty looks balanced instead of clinging to a corner.
    """

    def __init__(self, rows, cols, area, margin=18):
        x, y, w, h = area
        cell = min((w - 2 * margin) // cols, (h - 2 * margin) // rows)
        self.cell_size = max(8, int(cell))
        grid_w = cols * self.cell_size
        grid_h = rows * self.cell_size
        self.ox = x + (w - grid_w) // 2
        self.oy = y + (h - grid_h) // 2
        self.width = grid_w
        self.height = grid_h

    def origin(self, row, col):
        s = self.cell_size
        return (self.ox + col * s, self.oy + row * s)

    def center(self, row, col):
        s = self.cell_size
        return (self.ox + col * s + s / 2, self.oy + row * s + s / 2)


def ease(current, target, factor):
    """Move ``current`` a fraction ``factor`` of the way toward ``target``."""
    return current + (target - current) * factor


def pulse(t, speed=2.0, lo=0.0, hi=1.0):
    """A smooth sine oscillation between ``lo`` and ``hi``."""
    return lo + (hi - lo) * (0.5 + 0.5 * math.sin(t * speed))


# --------------------------------------------------------------------------- #
# Background
# --------------------------------------------------------------------------- #
def make_gradient(width, height, top, bottom):
    """Return a pre-rendered vertical gradient surface."""
    surface = pygame.Surface((width, height))
    for y in range(height):
        f = y / max(1, height - 1)
        color = (
            int(top[0] + (bottom[0] - top[0]) * f),
            int(top[1] + (bottom[1] - top[1]) * f),
            int(top[2] + (bottom[2] - top[2]) * f),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    return surface


class Starfield:
    """A drifting, twinkling field of stars for the menu backgrounds."""

    def __init__(self, count=90):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                "x": random.uniform(0, config.WIDTH),
                "y": random.uniform(0, config.HEIGHT),
                "speed": random.uniform(4, 22),
                "size": random.choice([1, 1, 1, 2, 2, 3]),
                "phase": random.uniform(0, math.tau),
            })

    def draw(self, surface, t):
        for s in self.stars:
            y = (s["y"] + t * s["speed"]) % config.HEIGHT
            twinkle = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 2.5 + s["phase"]))
            v = int(90 + 150 * twinkle)
            color = (min(255, v - 20), min(255, v), 255)
            pygame.draw.circle(surface, color, (int(s["x"]), int(y)), s["size"])


# --------------------------------------------------------------------------- #
# Glow
# --------------------------------------------------------------------------- #
_glow_cache = {}


def _glow_surface(radius, color):
    key = (radius, color)
    surf = _glow_cache.get(key)
    if surf is not None:
        return surf

    d = radius * 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    layers = 6
    for i in range(layers, 0, -1):
        r = max(1, int(radius * i / layers))
        alpha = int(70 * (1 - (i - 1) / layers))
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
    _glow_cache[key] = surf
    return surf


def draw_glow(surface, color, center, radius):
    """Blit a soft radial glow centered on ``center``."""
    radius = max(1, int(radius))
    surf = _glow_surface(radius, tuple(color))
    surface.blit(surf, (int(center[0]) - radius, int(center[1]) - radius))


def draw_alpha_circle(surface, color, center, radius, alpha):
    radius = max(1, int(radius))
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, alpha), (radius, radius), radius)
    surface.blit(surf, (int(center[0]) - radius, int(center[1]) - radius))
