"""Small reusable drawing helpers shared across the game screens."""

import pygame

from . import config, effects

_GLOW_OFFSETS = [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]


def blit_centered(surface, font, text, color, y):
    """Render ``text`` horizontally centered at height ``y``."""
    label = font.render(text, True, color)
    surface.blit(label, ((config.WIDTH - label.get_width()) // 2, y))
    return label


def title(surface, font, text, color, y, glow_color=config.Color.ACCENT):
    """Render a centered title with a soft glowing halo."""
    base = font.render(text, True, color)
    halo = font.render(text, True, glow_color)
    halo.set_alpha(55)
    x = (config.WIDTH - base.get_width()) // 2
    for dx, dy in _GLOW_OFFSETS:
        surface.blit(halo, (x + dx, y + dy))
    surface.blit(base, (x, y))
    return base


def draw_overlay(surface, alpha=180):
    """Darken the whole screen (used behind modal screens)."""
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
    overlay.set_alpha(alpha)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))


def panel(surface, rect, radius=16, fill=config.Color.PANEL, border=config.Color.PANEL_BORDER):
    """A rounded, bordered panel with a soft drop shadow."""
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 110), shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, (rect.x, rect.y + 6))
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=radius)


def button(surface, font, x, y, w, h, text):
    """Draw an animated button and return True while it is being clicked."""
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]

    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse)
    draw_rect = rect.inflate(10, 8) if hovered else rect

    # drop shadow
    shadow = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=14)
    surface.blit(shadow, (draw_rect.x, draw_rect.y + 5))

    if hovered:
        effects.draw_glow(surface, config.Color.ACCENT, draw_rect.center, draw_rect.width // 2)

    color = config.Color.BTN_HOVER if hovered else config.Color.BTN
    border = config.Color.ACCENT if hovered else config.Color.BTN_BORDER
    pygame.draw.rect(surface, color, draw_rect, border_radius=14)
    pygame.draw.rect(surface, border, draw_rect, width=2, border_radius=14)

    label = font.render(text, True, config.Color.WHITE)
    surface.blit(label, (draw_rect.centerx - label.get_width() // 2,
                         draw_rect.centery - label.get_height() // 2))

    return hovered and clicked
