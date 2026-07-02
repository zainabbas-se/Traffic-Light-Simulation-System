"""Streamlit dashboard for the Petri net traffic intersection simulator."""

from __future__ import annotations

import time

import streamlit as st

from ui_components import (
    inject_styles,
    render_header,
    render_kpis,
    render_petri_net_diagram,
    render_sidebar,
)
from utils import get_cycle_speed, get_engine, get_rerun_poll_seconds, set_last_tick_now, should_auto_step


st.set_page_config(
    page_title="Smart Traffic Intersection Simulator",
    page_icon="traffic_light",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
engine = get_engine()

pedestrian_exit_completed = engine.process_pending_pedestrian_exit()
if pedestrian_exit_completed:
    set_last_tick_now()

if (
    engine.is_running
    and not pedestrian_exit_completed
    and should_auto_step(get_cycle_speed())
):
    engine.run_step()
    set_last_tick_now()

marking = engine.net.marking_as_dict()
current_light = engine.net.current_light()

with st.sidebar:
    render_sidebar(engine, current_light)

# Row 1: project identity and purpose.
render_header()

# Row 2: high-level operating metrics.
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
render_kpis(marking, current_light)
st.markdown("</div>", unsafe_allow_html=True)

# Row 3: Petri net structure and current marking.
st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
render_petri_net_diagram(engine.net)
st.markdown("</div>", unsafe_allow_html=True)
if engine.is_running or engine.pending_pedestrian_exit_at is not None:
    time.sleep(get_rerun_poll_seconds())
    st.rerun()

