# Streamlit Traffic Simulation

Web dashboard implementation of the Traffic Light Simulation System. It models an intersection with a Petri net and exposes controls, KPIs, live signal state, and an activity log through Streamlit.

## Features

- Petri net places, transitions, tokens, and firing rules
- Red -> green -> yellow -> red signal cycle
- Add car and pedestrian request controls
- Manual step, start, pause, and reset controls
- Streamlit session state for persistent simulation state
- Responsive dashboard with traffic light visualization and event log

## Requirements

- Python 3.10 or newer
- Streamlit 1.36.0 or newer

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
|-- ui_components.py
|-- utils.py
|-- requirements.txt
`-- README.md
```

## Simulation Priority

Each automatic or manual step follows this order:

1. Complete a scheduled pedestrian crossing.
2. Start pedestrian crossing when a pedestrian is waiting and the light is red.
3. Allow one car to pass when the light is green and cars are waiting.
4. Otherwise, advance the normal traffic light cycle.