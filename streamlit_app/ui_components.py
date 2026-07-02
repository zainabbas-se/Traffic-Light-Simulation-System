"""Reusable Streamlit UI components for the traffic simulator."""

from __future__ import annotations

import html

import streamlit as st

from diagram import build_figure
from petri_net import PetriNet

LIGHT_COLORS = {
    "Red": "#ef4444",
    "Yellow": "#facc15",
    "Green": "#22c55e",
}

ICON_CAR = "&#128663;"
ICON_CHECK = "&#9989;"
ICON_PEDESTRIAN = "&#128694;"
ICON_LIGHT = "&#128678;"
ICON_GREEN = "&#128994;"
ICON_YELLOW = "&#128993;"
ICON_RED = "&#128308;"
ICON_GEAR = "&#9881;"


def inject_styles() -> None:
    """Add dashboard styling while keeping the page Streamlit-native."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, "Segoe UI", sans-serif;
}

*, *::before, *::after {
    box-sizing: border-box;
}

html, body, .stApp {
    max-width: 100%;
    overflow-x: hidden;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(14, 165, 233, 0.10), transparent 30rem),
        linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
    max-width: 78.75rem;
    width: 100%;
}

.dashboard-header {
    background: #0f172a;
    color: #ffffff;
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.16);
    width: 100%;
    max-width: 100%;
    min-height: 5.5rem;
    display: flex;
    align-items: center;
}

.dashboard-title {
    font-size: 1.9rem;
    line-height: 1.25;
    font-weight: 800;
    margin: 0;
    padding: 0;
    overflow-wrap: anywhere;
}

.section-title {
    color: #0f172a;
    font-size: 1rem;
    font-weight: 800;
    margin: 0 0 10px 0;
}

.section-subtitle {
    color: #64748b;
    font-size: 0.82rem;
    margin: 0 0 12px 0;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 20px;
    margin-bottom: 24px;
    width: 100%;
    max-width: 100%;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 18px;
    min-height: 104px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
    position: relative;
    overflow: hidden;
    width: 100%;
    max-width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.kpi-topline {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    position: relative;
    z-index: 1;
    min-width: 0;
}

.kpi-icon {
    width: 2.125rem;
    height: 2.125rem;
    min-width: 2.125rem;
    display: grid;
    place-items: center;
    border-radius: 8px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 1.05rem;
}

.kpi-label {
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 800;
    overflow-wrap: anywhere;
}

.kpi-value {
    color: #0f172a;
    font-size: clamp(1.35rem, 2vw, 1.75rem);
    line-height: 1;
    font-weight: 800;
    position: relative;
    z-index: 1;
    overflow-wrap: anywhere;
}

.dashboard-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
    width: 100%;
    max-width: 100%;
    height: 100%;
    overflow: hidden;
}

.top-row-card {
    height: 28rem;
    min-height: 28rem;
    display: flex;
    flex-direction: column;
}

.traffic-card-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    min-height: 0;
    gap: 12px;
    width: 100%;
    max-width: 100%;
}

.traffic-shell {
    width: min(100%, 7.4rem);
    background: linear-gradient(145deg, #111827, #020617);
    border-radius: 8px;
    padding: 0.85rem 0.8rem;
    border: 5px solid #334155;
    box-shadow:
        inset 0 0 18px rgba(255, 255, 255, 0.08),
        0 18px 30px rgba(15, 23, 42, 0.22);
}

.traffic-cap {
    width: 3.6rem;
    height: 0.6rem;
    background: #334155;
    border-radius: 8px 8px 0 0;
    margin: 0 auto -2px auto;
}

.lamp-pocket {
    width: 5rem;
    height: 5rem;
    border-radius: 50%;
    margin: 0.5rem auto;
    background: #020617;
    display: grid;
    place-items: center;
    box-shadow: inset 0 4px 14px rgba(0, 0, 0, 0.75);
}

.lamp {
    width: 3.85rem;
    height: 3.85rem;
    border-radius: 50%;
    opacity: 0.22;
    border: 3px solid rgba(255, 255, 255, 0.22);
    background:
        radial-gradient(circle at 35% 30%, rgba(255, 255, 255, 0.42), transparent 22px),
        var(--lamp-color);
}

.lamp.active {
    opacity: 1;
    box-shadow:
        0 0 22px 7px var(--glow),
        inset 0 0 10px rgba(255, 255, 255, 0.28);
}

.traffic-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    background: #f8fafc;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    font-weight: 800;
}

.status-dot {
    width: 0.7rem;
    height: 0.7rem;
    border-radius: 50%;
    background: var(--active-color);
    box-shadow: 0 0 14px var(--active-color);
}

.activity-log {
    flex: 1;
    min-height: 0;
    max-height: none;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 4px;
    width: 100%;
    max-width: 100%;
}

.activity-card {
    display: flex;
    flex-direction: column;
}

.event-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 11px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #f8fafc;
    margin-bottom: 8px;
}

.event-row.latest {
    background: #ecfeff;
    border-color: #67e8f9;
    box-shadow: 0 8px 18px rgba(6, 182, 212, 0.12);
}

.event-badge {
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    flex: 0 0 auto;
}

.event-text {
    color: #0f172a;
    font-size: 0.9rem;
    font-weight: 800;
    line-height: 1.35;
    overflow-wrap: anywhere;
}

.event-meta {
    color: #64748b;
    font-size: 0.74rem;
    font-weight: 800;
    margin-top: 2px;
}

.empty-log {
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    color: #64748b;
    padding: 24px;
    text-align: center;
    background: #f8fafc;
    flex: 1;
    display: grid;
    place-items: center;
}

div.stButton > button {
    width: 100%;
    max-width: 100%;
    min-height: 42px;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    color: #0f172a;
    font-weight: 800;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

div.stButton > button:hover {
    border-color: #0284c7;
    color: #075985;
    background: #f0f9ff;
}

div.stButton > button:focus:not(:active) {
    border-color: #0284c7;
    color: #075985;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.18);
}

.dashboard-section {
    margin-bottom: 24px;
    width: 100%;
    max-width: 100%;
}

@media (min-width: 1200px) {
    .kpi-grid {
        grid-template-columns: repeat(5, minmax(0, 1fr));
    }
}

@media (min-width: 768px) and (max-width: 1199px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .kpi-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .dashboard-title {
        font-size: 1.6rem;
    }

}

@media (max-width: 767px) {
    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .dashboard-header {
        padding: 18px;
        min-height: 4.75rem;
    }

    .dashboard-title {
        font-size: 1.35rem;
        line-height: 1.3;
    }

    .kpi-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }

    .kpi-card {
        min-height: 92px;
    }

    .dashboard-card {
        padding: 18px;
    }

    .activity-card .activity-log {
        max-height: 18rem;
        min-height: 12rem;
    }

    .traffic-card-inner {
        min-height: auto;
    }

    .traffic-shell {
        width: 6.7rem;
        padding: 0.7rem;
    }

    .lamp-pocket {
        width: 4.4rem;
        height: 4.4rem;
    }

    .lamp {
        width: 3.35rem;
        height: 3.35rem;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the dashboard title and project description."""
    st.markdown(
        '<div class="dashboard-header">'
        '<div class="dashboard-title">'
        "Smart Traffic Intersection Simulator Using Petri Nets"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_card_header(title: str, subtitle: str | None = None) -> None:
    """Render a compact card title used above Streamlit-native widgets."""
    subtitle_markup = (
        f'<div class="section-subtitle">{html.escape(subtitle)}</div>'
        if subtitle
        else ""
    )
    st.markdown(
        f'<div class="section-title">{html.escape(title)}</div>{subtitle_markup}',
        unsafe_allow_html=True,
    )


def render_kpis(marking: dict[str, int], current_light: str) -> None:
    """Render the five required KPI cards."""
    values = [
        (ICON_CAR, "Cars Waiting", marking["Cars Waiting"], "#f59e0b", "#fffbeb"),
        (ICON_CHECK, "Cars Passed", marking["Car Passed"], "#16a34a", "#f0fdf4"),
        (
            ICON_PEDESTRIAN,
            "Pedestrian Waiting",
            marking["Pedestrian Waiting"],
            "#0891b2",
            "#ecfeff",
        ),
        (
            ICON_PEDESTRIAN,
            "Pedestrian Crossing",
            marking["Pedestrian Crossing"],
            "#0284c7",
            "#eff6ff",
        ),
        (ICON_LIGHT, "Current Traffic Light", current_light, "#dc2626", "#fef2f2"),
    ]
    cards = []
    for icon, label, value, accent, accent_soft in values:
        cards.append(
            '<div class="kpi-card" '
            f'style="--accent:{accent}; --accent-soft:{accent_soft};">'
            '<div class="kpi-topline">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div>'
            "</div>"
            f'<div class="kpi-value">{value}</div>'
            "</div>"
        )
    st.markdown(
        f'<div class="kpi-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_traffic_light(current_light: str) -> None:
    """Render a CSS traffic light with the active lamp glowing."""
    lamps = []
    for light in ("Red", "Yellow", "Green"):
        active_class = "active" if current_light == light else ""
        color = LIGHT_COLORS[light]
        lamps.append(
            '<div class="lamp-pocket">'
            f'<div class="lamp {active_class}" '
            f'style="--lamp-color:{color}; --glow:{color};" '
            f'title="{light} Light"></div>'
            "</div>"
        )

    active_color = LIGHT_COLORS.get(current_light, "#64748b")
    st.markdown(
        '<div class="dashboard-card top-row-card traffic-card">'
        '<div class="section-title">Traffic Light</div>'
        '<div class="traffic-card-inner">'
        "<div>"
        '<div class="traffic-cap"></div>'
        f'<div class="traffic-shell">{"".join(lamps)}</div>'
        "</div>"
        f'<div class="traffic-status-pill" style="--active-color:{active_color};">'
        '<span class="status-dot"></span>'
        f"Active light: {current_light}"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_petri_net_diagram(net: PetriNet) -> None:
    """Render the live Petri net graph with the current token marking."""
    with st.container(border=True):
        render_card_header("Petri Net Diagram")
        fig = build_figure(net)
        st.pyplot(fig, clear_figure=True, use_container_width=True)


def render_activity_card(entries: list[str]) -> None:
    """Render the activity log in a fixed-height card with internal scroll."""
    st.markdown(
        '<div class="dashboard-card top-row-card activity-card">'
        '<div class="section-title">Activity Log</div>'
        '<div class="section-subtitle">'
        "Latest transition and user action events"
        "</div>"
        f"{activity_log_html(entries)}"
        "</div>",
        unsafe_allow_html=True,
    )



def activity_log_html(entries: list[str]) -> str:
    """Build the activity log markup."""
    if not entries:
        return (
            '<div class="activity-log">'
            '<div class="empty-log">'
            "No events yet. Use the controls or start the simulation."
            "</div>"
            "</div>"
        )

    rows = []
    for index, entry in enumerate(entries[:30]):
        safe_entry = html.escape(entry)
        latest_class = " latest" if index == 0 else ""
        icon = event_icon(entry)
        label = "Latest event" if index == 0 else "Event"
        rows.append(
            f'<div class="event-row{latest_class}">'
            f'<div class="event-badge">{icon}</div>'
            "<div>"
            f'<div class="event-text">{safe_entry}</div>'
            f'<div class="event-meta">{label}</div>'
            "</div>"
            "</div>"
        )

    return f'<div class="activity-log">{"".join(rows)}</div>'


def event_icon(entry: str) -> str:
    """Return a compact visual badge for a log event."""
    lowered = entry.lower()
    if "car" in lowered:
        return ICON_CAR
    if "pedestrian" in lowered:
        return ICON_PEDESTRIAN
    if "green" in lowered:
        return ICON_GREEN
    if "yellow" in lowered:
        return ICON_YELLOW
    if "red" in lowered:
        return ICON_RED
    if "exec" in lowered:
        return ICON_GEAR
    return "&bull;"
