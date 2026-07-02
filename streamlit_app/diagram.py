"""
diagram.py
=========================================================================
Renders the Petri Net (places, transitions, arcs, and the current
token marking) as a matplotlib Figure. Streamlit displays this via
`st.image(...)`, so the diagram simply gets redrawn from scratch every
rerun using whatever the current `net.marking` is — no manual canvas
bookkeeping needed like a desktop GUI would require.
=========================================================================
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from diagram_layout import (
    ALL_NODE_POSITIONS,
    ARCS_DEF,
    COLOR_ARC,
    COLOR_HIGHLIGHT,
    COLOR_PLACE_BORDER,
    COLOR_PLACE_FILL,
    COLOR_TEXT_BOLD,
    COLOR_TEXT_DIM,
    COLOR_TRANS_FILL,
    CURVED_ARC_RAD,
    DASHED_ARCS,
    PLACE_LABELS,
    PLACE_POS,
    PLACE_RADIUS,
    SECTIONS,
    TOKEN_COLOR_FOR_PLACE,
    TRANS_BAR_LENGTH,
    TRANS_BAR_THICK,
    TRANS_LABEL_ANCHOR,
    TRANS_ORIENT,
    TRANS_POS,
    TRANSITION_LABELS,
)
from petri_net import PetriNet


def _transition_bounds(name: str, x: float, y: float) -> tuple[float, float, float, float]:
    """Return x, y, width, height for a classic Petri net transition bar."""
    if TRANS_ORIENT.get(name, "v") == "h":
        return (
            x - TRANS_BAR_LENGTH / 2,
            y - TRANS_BAR_THICK / 2,
            TRANS_BAR_LENGTH,
            TRANS_BAR_THICK,
        )
    return (
        x - TRANS_BAR_THICK / 2,
        y - TRANS_BAR_LENGTH / 2,
        TRANS_BAR_THICK,
        TRANS_BAR_LENGTH,
    )


def _edge_point(node_name: str, toward_xy: tuple[float, float]) -> tuple[float, float]:
    """Point on a place circle or transition bar facing `toward_xy`."""
    x0, y0 = ALL_NODE_POSITIONS[node_name]
    tx, ty = toward_xy
    dx, dy = tx - x0, ty - y0
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return (x0, y0)
    ux, uy = dx / dist, dy / dist

    if node_name in PLACE_POS:
        return (x0 + ux * PLACE_RADIUS, y0 + uy * PLACE_RADIUS)

    bx, by, bw, bh = _transition_bounds(node_name, x0, y0)
    half_w, half_h = bw / 2, bh / 2
    tx_limit = (half_w / abs(ux)) if abs(ux) > 1e-9 else 1e9
    ty_limit = (half_h / abs(uy)) if abs(uy) > 1e-9 else 1e9
    t = min(tx_limit, ty_limit)
    return (x0 + ux * t, y0 + uy * t)


TOKEN_OFFSETS: dict[int, list[tuple[float, float]]] = {
    1: [(0, 0)],
    2: [(-0.2, 0), (0.2, 0)],
    3: [(-0.2, -0.14), (0.2, -0.14), (0, 0.18)],
    4: [(-0.2, -0.16), (0.2, -0.16), (-0.2, 0.16), (0.2, 0.16)],
}


def _draw_sections(ax: plt.Axes) -> None:
    """Background panels that group the three parts of the intersection."""
    for section in SECTIONS:
        x, y = section["xy"]  # type: ignore[misc]
        box = Rectangle(
            (x, y),
            section["width"],  # type: ignore[arg-type]
            section["height"],  # type: ignore[arg-type]
            facecolor=section["fill"],  # type: ignore[arg-type]
            edgecolor=section["edge"],  # type: ignore[arg-type]
            linewidth=1.2,
            zorder=0,
        )
        ax.add_patch(box)
        ax.text(
            x + 0.25,
            y + section["height"] - 0.22,  # type: ignore[operator]
            str(section["title"]),
            ha="left",
            va="top",
            fontsize=10,
            fontweight="bold",
            color=COLOR_TEXT_BOLD,
            zorder=1,
        )


def _draw_legend(ax: plt.Axes) -> None:
    """Short key so readers know what shapes mean."""
    ax.text(
        0.55,
        0.08,
        "○ circle = state (place)     | bar = action (transition)     ● dot = token",
        ha="left",
        va="center",
        fontsize=9,
        color=COLOR_TEXT_DIM,
        zorder=1,
    )


def _draw_transitions(ax: plt.Axes, last_fired: str | None) -> None:
    """Draw transition bars with short labels beside each bar."""
    label_bbox = {
        "boxstyle": "round,pad=0.12",
        "facecolor": "white",
        "edgecolor": "#e2e8f0",
        "linewidth": 0.5,
        "alpha": 0.92,
    }

    for name, (x, y) in TRANS_POS.items():
        highlighted = name == last_fired
        bx, by, bw, bh = _transition_bounds(name, x, y)
        ax.add_patch(
            Rectangle(
                (bx, by),
                bw,
                bh,
                facecolor=COLOR_HIGHLIGHT if highlighted else COLOR_TRANS_FILL,
                edgecolor=COLOR_HIGHLIGHT if highlighted else COLOR_TRANS_FILL,
                linewidth=1.2 if highlighted else 0,
                zorder=4,
            )
        )

        label = TRANSITION_LABELS.get(name, name)
        dx, dy, ha, va = TRANS_LABEL_ANCHOR.get(name, (0, -0.38, "center", "top"))
        ax.text(
            x + dx,
            y + dy,
            label,
            ha=ha,
            va=va,
            fontsize=6.8,
            color=COLOR_TEXT_DIM,
            fontweight="600",
            zorder=5,
            bbox=label_bbox,
        )


def build_figure(net: PetriNet, last_fired: str | None = None) -> plt.Figure:
    """Return a matplotlib Figure for the current state of `net`."""
    fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=130)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    _draw_sections(ax)

    for src, dest in ARCS_DEF:
        p1 = _edge_point(src, ALL_NODE_POSITIONS[dest])
        p2 = _edge_point(dest, ALL_NODE_POSITIONS[src])
        dashed = (src, dest) in DASHED_ARCS
        curve = CURVED_ARC_RAD.get((src, dest))
        connectionstyle = f"arc3,rad={curve}" if curve is not None else "arc3,rad=0"
        arrow = FancyArrowPatch(
            p1,
            p2,
            arrowstyle="-|>" if not dashed else "-",
            mutation_scale=11,
            color=COLOR_ARC,
            linewidth=1.3,
            linestyle=(0, (4, 4)) if dashed else "solid",
            connectionstyle=connectionstyle,
            zorder=2,
        )
        ax.add_patch(arrow)

    _draw_transitions(ax, last_fired)

    for name, (x, y) in PLACE_POS.items():
        ax.add_patch(
            Circle(
                (x, y),
                PLACE_RADIUS,
                facecolor=COLOR_PLACE_FILL,
                edgecolor=COLOR_PLACE_BORDER,
                linewidth=2,
                zorder=5,
            )
        )
        ax.text(
            x,
            y - PLACE_RADIUS - 0.28,
            PLACE_LABELS.get(name, name),
            ha="center",
            va="top",
            fontsize=8.5,
            color=COLOR_TEXT_DIM,
            zorder=6,
        )

        count = int(net.marking[name])
        if count > 0:
            color = TOKEN_COLOR_FOR_PLACE.get(name, "#94a3b8")
            if count <= 4:
                for dx, dy in TOKEN_OFFSETS[count]:
                    ax.add_patch(
                        Circle(
                            (x + dx, y + dy),
                            0.12,
                            facecolor=color,
                            edgecolor="white",
                            linewidth=1,
                            zorder=7,
                        )
                    )
            else:
                ax.add_patch(
                    Circle(
                        (x, y),
                        0.24,
                        facecolor=color,
                        edgecolor="white",
                        linewidth=1,
                        zorder=7,
                    )
                )
                ax.text(
                    x,
                    y,
                    str(count),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                    zorder=8,
                )

    _draw_legend(ax)
    fig.tight_layout(pad=0.3)
    return fig
