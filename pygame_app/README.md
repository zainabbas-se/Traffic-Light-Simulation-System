# Pygame Traffic Simulation

Desktop Pygame implementation of the Traffic Light Simulation System. It animates cars, pedestrians, a crosswalk, a traffic signal, and a HUD inside a resizable window.

## Features

- Automatic red -> yellow -> green -> yellow signal cycle
- Cars move during green phases and queue when needed
- Pedestrians cross during red phases
- Safety-aware phase transitions
- Resizable desktop window with live counters

## Requirements

- Python 3.11 or newer
- Pygame 2.5.0 or newer

## Setup

```bash
cd pygame_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

From `pygame_app/`:

```bash
python main.py
```

From the repository root:

```bash
python pygame_app/main.py
```

The window closes automatically after the configured runtime in `app.py`. Press `Esc` or close the window to quit early.

## Structure

```text
pygame_app/
|-- app.py
|-- simulation.py
|-- ui.py
|-- main.py
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## File Overview

| Path | Purpose |
| --- | --- |
| `main.py` | Entry point for the Pygame app |
| `app.py` | Pygame window, event loop, timing, and draw/update wiring |
| `simulation.py` | Core simulation model for lights, cars, pedestrians, spawning, and pruning |
| `ui.py` | Rendering for the road, crosswalk, traffic signal, sprites, queue, and HUD |
| `requirements.txt` | Pygame dependency list |
| `pyproject.toml` | Pygame app metadata |
