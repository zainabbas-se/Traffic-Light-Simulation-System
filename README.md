# Traffic Light Simulation System

A dual-implementation traffic light simulation repository containing two independent applications:

- **Pygame App**: a desktop animation of cars, pedestrians, traffic lights, crosswalks, and live HUD counters.
- **Streamlit App**: a web dashboard that models a smart traffic intersection with Petri net places, transitions, tokens, a live diagram, and interactive controls.

Each implementation has its own source files, dependencies, and README so both apps can be installed and run separately.

## Features

- Two independent implementations in one repository
- Flat, matching app folders for Pygame and Streamlit
- Separate dependency files for each implementation
- Desktop simulation with automatic signal timing and animated traffic flow
- Web dashboard with Petri net diagram, KPIs, sidebar controls, and configurable cycle speed

## Folder Structure

```text
Traffic-Light-Simulation-System/
|-- pygame_app/
|   |-- app.py
|   |-- simulation.py
|   |-- ui.py
|   |-- main.py
|   |-- pyproject.toml
|   |-- requirements.txt
|   `-- README.md
|-- streamlit_app/
|   |-- app.py
|   |-- petri_net.py
|   |-- simulation_engine.py
|   |-- diagram.py
|   |-- diagram_layout.py
|   |-- ui_components.py
|   |-- utils.py
|   |-- requirements.txt
|   `-- README.md
|-- .gitignore
`-- README.md
```

## Run the Pygame Version

From the repository root:

```bash
cd pygame_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

You can also run it directly from the repository root after installing dependencies:

```bash
python pygame_app/main.py
```

## Run the Streamlit Version

From the repository root:

```bash
cd streamlit_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

You can also run it directly from the repository root after installing dependencies:

```bash
streamlit run streamlit_app/app.py
```

Streamlit will print the local URL in the terminal, usually `http://localhost:8501`.

## Technology Comparison

| Area | Pygame Implementation | Streamlit Implementation |
| --- | --- | --- |
| Interface | Desktop window | Browser dashboard |
| Main command | `python main.py` | `streamlit run app.py` |
| Direct root command | `python pygame_app/main.py` | `streamlit run streamlit_app/app.py` |
| Core focus | Animation and real-time visual movement | Petri net state modeling, diagram, and interactive controls |
| Dependency file | `pygame_app/requirements.txt` | `streamlit_app/requirements.txt` |
| Best for | Visual simulation demos | Explanation, analysis, and web presentation |
| Runtime model | Game loop with frame updates | Streamlit reruns with session state |

## Development Notes

- Keep Pygame-only code inside `pygame_app/`.
- Keep Streamlit-only code inside `streamlit_app/`.
- Install dependencies from the app folder you want to run.
- Do not share runtime dependencies through a root `requirements.txt`; each app owns its dependency list.
