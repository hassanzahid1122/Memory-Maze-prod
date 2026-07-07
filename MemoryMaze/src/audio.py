"""Procedurally-synthesized sound effects and music — no asset files.

All tones are generated at startup into pygame Sound buffers. Everything is
defensive: if the machine has no audio device the whole module quietly becomes
a set of no-ops so the game still runs.
"""

import math
from array import array

import pygame

_RATE = 44100
_channels = 1
_ready = False
_enabled = True
_sfx = {}
_music_channel = None
_music_sound = None


# --------------------------------------------------------------------------- #
# Synthesis
# --------------------------------------------------------------------------- #
def _tone(freq, ms, vol=0.5, wave="sine"):
    n = max(1, int(_RATE * ms / 1000))
    amp = 32767 * vol
    attack = max(1, int(_RATE * 0.005))
    release = max(1, int(_RATE * 0.030))
    out = []
    for i in range(n):
        phase = 2 * math.pi * freq * (i / _RATE)
        s = 1.0 if math.sin(phase) >= 0 else -1.0 if wave == "square" else math.sin(phase)
        env = min(1.0, i / attack, (n - i) / release)
        out.append(int(amp * s * env))
    return out


def _silence(ms):
    return [0] * int(_RATE * ms / 1000)


def _make(samples):
    if _channels == 2:
        doubled = []
        for s in samples:
            doubled.append(s)
            doubled.append(s)
        samples = doubled
    return pygame.mixer.Sound(buffer=array("h", samples).tobytes())


def _seq(*chunks):
    out = []
    for c in chunks:
        out.extend(c)
    return out


# --------------------------------------------------------------------------- #
# Lifecycle
# --------------------------------------------------------------------------- #
def init(enabled=True):
    global _ready, _enabled, _channels
    _enabled = enabled
    if _ready:
        return
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=_RATE, size=-16, channels=1, buffer=512)
        info = pygame.mixer.get_init()
        _channels = info[2] if info else 1
    except pygame.error:
        _ready = False
        return

    _sfx["move"] = _make(_tone(320, 32, 0.18, "square"))
    _sfx["pickup"] = _make(_seq(_tone(523, 70, 0.4), _tone(659, 70, 0.4), _tone(784, 110, 0.4)))
    _sfx["win"] = _make(_seq(_tone(523, 120, 0.5), _tone(659, 120, 0.5),
                             _tone(784, 120, 0.5), _tone(1047, 200, 0.5)))
    _sfx["lose"] = _make(_seq(_tone(300, 160, 0.45, "square"), _tone(200, 260, 0.45, "square")))
    _sfx["tick"] = _make(_tone(660, 70, 0.35))
    _sfx["go"] = _make(_seq(_tone(784, 90, 0.5), _tone(1175, 220, 0.5)))
    for s in _sfx.values():
        s.set_volume(0.6)

    _build_music()
    _ready = True


def _build_music():
    """A slow, quiet ambient pad loop (root + fifth + octave)."""
    global _music_sound
    length = int(_RATE * 6)
    freqs = (110.0, 164.81, 220.0)
    out = []
    for i in range(length):
        t = i / _RATE
        lfo = 0.5 + 0.5 * math.sin(2 * math.pi * 0.1 * t)  # gentle swell
        v = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
        out.append(int(32767 * 0.12 * lfo * v))
    _music_sound = _make(out)
    _music_sound.set_volume(0.35)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def set_enabled(value):
    global _enabled
    _enabled = value
    if not value:
        stop_music()


def play(name):
    if _ready and _enabled and name in _sfx:
        _sfx[name].play()


def start_music():
    global _music_channel
    if _ready and _enabled and _music_sound and _music_channel is None:
        _music_channel = _music_sound.play(loops=-1, fade_ms=800)


def stop_music():
    global _music_channel
    if _music_channel is not None:
        _music_channel.fadeout(400)
        _music_channel = None
