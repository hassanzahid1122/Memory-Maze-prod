# Memory Maze

A race-the-AI maze game built with **pygame**. You and an A\*-driven AI both start
at the top-left and race to the bottom-right exit — but the maze periodically
*hides* most of its cells, so you have to memorise the layout. Grab power-ups to
speed yourself up or slow the AI down.

## Gameplay

- **Move:** arrow keys
- **Pause:** `Esc` &nbsp;·&nbsp; **Resume:** `Esc`, **Restart:** `R`, **Menu:** `M`
- **Power-ups:** `SPEED` (you move faster), `SLOW_AI` (AI slows down), `FREEZE` (AI freezes)
- **Penalty:** walking into a dead-end adds time to your score.

## Project layout

```
MemoryMaze/
├── main.py              # entry point
├── memory_maze.spec     # PyInstaller build spec
├── requirements.txt     # runtime dependency (pygame)
├── requirements-dev.txt # + PyInstaller for building the executable
└── src/
    ├── config.py        # all tunables, colors and difficulty presets
    ├── game.py          # window + screen state machine
    ├── maze.py          # maze generation, memory cycle, rendering
    ├── player.py        # human player
    ├── ai.py            # A* AI opponent
    ├── powerups.py      # power-up spawning & effects
    ├── scores.py        # leaderboard persistence
    └── ui.py            # shared drawing helpers
```

## Run from source

```bash
cd MemoryMaze
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build a standalone executable

PyInstaller produces a single self-contained binary. **You must build on the OS
you want to target** — building on Windows gives a `.exe`, on Linux an ELF
binary, on macOS a Mac app. (PyInstaller does not cross-compile.)

```bash
cd MemoryMaze
pip install -r requirements-dev.txt
pyinstaller memory_maze.spec
```

The result appears in `dist/`:

- Windows → `dist/MemoryMaze.exe`
- Linux &nbsp;&nbsp;→ `dist/MemoryMaze`
- macOS &nbsp;&nbsp;→ `dist/MemoryMaze`

`scores.json` is created next to the executable the first time a game finishes.
