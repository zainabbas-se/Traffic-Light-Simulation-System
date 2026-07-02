"""Streamlit dashboard for the Petri net traffic intersection simulator."""

from __future__ import annotations

import time

import streamlit as st

from simulation_engine import AUTO_STEP_INTERVAL_SECONDS
from ui_components import (
    inject_styles,
    render_activity_card,
    render_card_header,
    render_header,
    render_kpis,
    render_petri_net_diagram,
    render_traffic_light,
)
from utils import get_engine, set_last_tick_now, should_auto_step


st.set_page_config(
    page_title="Smart Traffic Intersection Simulator",
    page_icon="traffic_light",
    layout="wide",
)

inject_styles()
engine = get_engine()

pedestrian_exit_completed = engine.process_pending_pedestrian_exit()
if pedestrian_exit_completed:
    set_last_tick_now()

if (
    engine.is_running
    and not pedestrian_exit_completed
    and should_auto_step(AUTO_STEP_INTERVAL_SECONDS)
):
    engine.run_step()
    set_last_tick_now()

# Row 1: project identity and purpose.
render_header()

# Row 2: high-level operating metrics.
marking = engine.net.marking_as_dict()
current_light = engine.net.current_light()
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
render_kpis(marking, current_light)
st.markdown("</div>", unsafe_allow_html=True)

# Row 3: Petri net structure and current marking.
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
render_petri_net_diagram(engine.net)
st.markdown("</div>", unsafe_allow_html=True)

# Row 4: live signal visualization and event feed.
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
traffic_column, log_column = st.columns([0.9, 1.35], gap="large")

with traffic_column:
    render_traffic_light(current_light)

with log_column:
    render_activity_card(list(engine.net.event_log))
st.markdown("</div>", unsafe_allow_html=True)

# Row 5: controls.
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
with st.container(border=True):
    render_card_header("Control Panel")
    control_a, control_b = st.columns(2)

    if control_a.button("Add Car", use_container_width=True):
        engine.add_car()
        st.rerun()

    if control_b.button("Pedestrian Request", use_container_width=True):
        engine.request_pedestrian()
        st.rerun()

    if control_a.button("Manual Step", use_container_width=True):
        engine.run_step()
        st.rerun()

    if control_b.button("Reset Simulation", use_container_width=True):
        engine.reset()
        set_last_tick_now()
        st.rerun()

    start_col, pause_col = st.columns(2)
    if start_col.button("Start Simulation", use_container_width=True):
        engine.is_running = True
        set_last_tick_now()
        st.rerun()

    if pause_col.button("Pause Simulation", use_container_width=True):
        engine.is_running = False
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if engine.is_running or engine.pending_pedestrian_exit_at is not None:
    time.sleep(0.5)
    st.rerun()