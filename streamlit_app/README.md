# Streamlit Traffic Simulation

Web dashboard implementation of the Traffic Light Simulation System. It models an intersection with a Petri net and exposes controls, KPIs, a live traffic light, and a live Petri net diagram through Streamlit.

## Features

- Petri net places, transitions, tokens, and firing rules
- Live Petri net diagram with labeled transitions and current marking
- Red -> green -> yellow -> red signal cycle
- Sidebar traffic light visualization with active lamp indicator
- Add car, pedestrian request, reset, and start simulation controls
- Configurable cycle speed (seconds per automatic step)
- Streamlit session state for persistent simulation state
- Responsive dashboard with KPI cards and sidebar control panel

## Requirements

- Python 3.10 or newer
- Streamlit 1.36.0 or newer
- Matplotlib 3.8.0 or newer

## Setup

```bash
cd streamlit_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Streamlit will print the local URL in the terminal, usually `http://localhost:8501`.

## Structure

```text
streamlit_app/
|-- app.py
|-- petri_net.py
|-- simulation_engine.py
|-- diagram.py
|-- diagram_layout.py
|-- ui_components.py
|-- utils.py
|-- requirements.txt
`-- README.md
```

## Dashboard Layout

- **Sidebar**: traffic light, cycle speed slider, and simulation controls
- **Main area**: project header, KPI cards, and Petri net diagram

## Simulation Priority

Each automatic step follows this order:

1. Complete a scheduled pedestrian crossing.
2. Start pedestrian crossing when a pedestrian is waiting and the light is red.
3. Allow one car to pass when the light is green and cars are waiting.
4. Otherwise, advance the normal traffic light cycle.
