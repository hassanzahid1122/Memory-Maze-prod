"""Small reusable drawing helpers shared across the game screens."""

import pygame

from . import config


def blit_centered(surface, font, text, color, y):
    """Render ``text`` horizontally centered at height ``y``."""
    label = font.render(text, True, color)
    surface.blit(label, ((config.WIDTH - label.get_width()) // 2, y))
    return label


def draw_overlay(surface, alpha=180):
    """Darken the whole screen (used behind modal screens)."""
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
    overlay.set_alpha(alpha)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))


def button(surface, font, x, y, w, h, text):
    """Draw a button and return True when it is being clicked."""
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]

    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse)

    color = config.Color.BTN_HOVER if hovered else config.Color.BTN
    pygame.draw.rect(surface, color, rect, border_radius=12)

    label = font.render(text, True, config.Color.WHITE)
    surface.blit(label, (x + (w - label.get_width()) // 2,
                         y + (h - label.get_height()) // 2))

    return hovered and clicked
