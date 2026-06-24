"""Utility helpers for Streamlit session state."""

from __future__ import annotations

import time

import streamlit as st

from simulation_engine import SimulationEngine


ENGINE_KEY = "traffic_engine"
LAST_TICK_KEY = "last_auto_tick"


def get_engine() -> SimulationEngine:
    """Create or return the current simulation engine from session state."""
    if ENGINE_KEY not in st.session_state:
        st.session_state[ENGINE_KEY] = SimulationEngine()
    return st.session_state[ENGINE_KEY]


def set_last_tick_now() -> None:
    """Remember the current time for auto-run pacing."""
    st.session_state[LAST_TICK_KEY] = time.time()


def should_auto_step(interval_seconds: float) -> bool:
    """Return True when enough time has passed for another automatic step."""
    last_tick = st.session_state.get(LAST_TICK_KEY, 0.0)
    return time.time() - float(last_tick) >= interval_seconds