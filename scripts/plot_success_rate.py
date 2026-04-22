"""
plot_success_rate.py
Generates one success-rate SVG bar chart per task.
Styled to match the Gated Memory Policy website palette.

Usage:
    cd /path/to/mem_website/scripts
    python plot_success_rate.py

Output (written under ../assets/charts/):
    cross_trial/pushing/success_rate.svg
    cross_trial/casting/success_rate.svg
    cross_trial/flinging/success_rate.svg
    in_trial/place_back_real/success_rate.svg
    in_trial/match_color/success_rate.svg
    in_trial/place_back/success_rate.svg
    mikasa_benchmark.svg
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Site palette (warm cream/beige — academic press tone) ───────────────────
BG         = "#faf7f0"   # matches site --bg (main page background)
TEXT       = "#2a2218"   # warm near-black, readable on cream
TEXT_MUTED = "#8a7a66"   # lighter warm brown-gray (softer, less heavy)
ACCENT     = "#b5552a"   # warm terracotta — matches site --accent
NEUTRAL    = "#d9cab0"   # lighter warm beige baseline bars (readable on cream)
BORDER     = "#e6d7bd"   # soft warm hairline

# ── Task definitions ──────────────────────────────────────────────────────────
# Each task defines its own `entries` list so you can freely add/remove methods.
#
# Entry format:
#   { "label": str,    # x-tick label (use \n for line break)
#     "value": float,  # success rate %
#     "err":   float,  # ± std (0 to omit error cap)
#     "ours":  bool }  # True → uses accent color + bold label
#
# Example with an extra baseline:
#   {"label": "Extra\nBaseline", "value": 35, "err": 3, "ours": False},

TASKS = {
    "cross_trial/pushing": [
        {"label": "nh-DP",       "value": 1,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 3,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 2,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 28,  "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 32,  "err": 0, "ours": False},
        {"label": "Ours", "value": 97,   "err": 0, "ours": True },
    ],
    "cross_trial/casting": [
        {"label": "nh-DP",       "value": 5,    "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 20,   "err": 0, "ours": False},
        {"label": "Ours", "value": 95,   "err": 0, "ours": True },
    ],
    "cross_trial/flinging": [
        {"label": "nh-DP",       "value": 54,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 54,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 54,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 65,   "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 69,   "err": 0, "ours": False},
        {"label": "Ours", "value": 81,   "err": 0, "ours": True },
    ],
    "in_trial/place_back_real": [
        {"label": "nh-DP",       "value": 10,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 62.5, "err": 0, "ours": False},
        {"label": "Ours", "value": 85,   "err": 0, "ours": True },
    ],
    "in_trial/match_color": [
        {"label": "nh-DP",       "value": 16,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 35,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 35,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 100,  "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 100,  "err": 0, "ours": False},
        {"label": "Ours", "value": 100,  "err": 0, "ours": True },
    ],
    "in_trial/place_back": [
        {"label": "nh-DP",       "value": 18,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 64,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 56,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 100,  "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 100,  "err": 0, "ours": False},
        {"label": "Ours", "value": 98,   "err": 0, "ours": True },
    ],
}

# ── Global font settings ──────────────────────────────────────────────────────
# svg.fonttype="none" emits real <text> elements; the browser then renders
# with its own font and correct space metrics. The default ("path") would
# outline every glyph and collapse space widths.
plt.rcParams.update({
    "font.family":        "sans-serif",
    "font.sans-serif":    ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype":       "none",
})

# ── Plotting ──────────────────────────────────────────────────────────────────
def plot_task(out_path: str, entries: list) -> None:
    labels  = [e["label"] for e in entries]
    values  = [e["value"] for e in entries]
    errors  = [e["err"]   for e in entries]
    is_ours = [e["ours"]  for e in entries]
    colors  = [ACCENT if o else NEUTRAL for o in is_ours]
    use_err = any(e > 0 for e in errors)

    n      = len(entries)
    fig_w  = 6.0
    # Taller canvas so the rotated y-label "Success Rate (%)" fits inside
    # the chart height at the larger font size without getting clipped.
    fig_h  = 4.2

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.set_facecolor(BG)
    ax.set_facecolor(BG)

    x     = np.arange(n)
    width = 0.65   # same visual weight regardless of bar count

    bars = ax.bar(
        x, values,
        width=width,
        color=colors,
        yerr=errors if use_err else None,
        error_kw=dict(elinewidth=0.8, capsize=2.2,
                      ecolor=TEXT_MUTED, capthick=0.8),
        zorder=3,
        linewidth=0,
    )

    # Horizontal title at top reads cleanly at any font size without the
    # viewBox-clipping issues a rotated y-label hits on narrow (~240px)
    # chart displays.
    ax.set_title("Success Rate (%)", fontsize=19, color=TEXT_MUTED,
                 pad=10, loc="left")

    ax.set_ylim(0, 118)
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(["0", "50", "100"], fontsize=20, color=TEXT_MUTED)

    # The chart displays at ~240px wide on the page. With 5-6 bars, any
    # horizontal or shallow-rotated label collides with its neighbor at a
    # readable font size. Use steeper rotation + smaller font for crowded
    # charts; keep wide horizontal labels for 3-bar charts (plenty of room).
    if n <= 3:
        rotation, xlabel_fs = 0, 22
    elif n == 4:
        rotation, xlabel_fs = 25, 20
    else:
        rotation, xlabel_fs = 38, 17
    rotate = rotation > 0

    ax.set_xticks(x)
    ax.set_xticklabels(
        labels,
        fontsize=xlabel_fs,
        color=TEXT,
        linespacing=1.2,
        rotation=rotation,
        ha="right" if rotate else "center",
        rotation_mode="anchor" if rotate else "default",
    )
    for tick, ours in zip(ax.get_xticklabels(), is_ours):
        if ours:
            tick.set_color(ACCENT)
            tick.set_fontweight("bold")

    # ylabel omitted: title above communicates the same thing and doesn't
    # suffer the narrow-chart vertical clipping problem.

    # ── Grid, spines, ticks ───────────────────────────────────────────────────
    ax.yaxis.grid(True, color=BORDER, linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["bottom"].set_linewidth(0.6)
    ax.tick_params(axis="both", length=0, pad=3)

    # ── Value labels above bars ───────────────────────────────────────────────
    err_pad = max(errors) if use_err else 0
    for bar, val, ours in zip(bars, values, is_ours):
        label_val = f"{int(val)}%" if val == int(val) else f"{val}%"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + err_pad + 1.5,
            label_val,
            ha="center", va="bottom",
            fontsize=20,
            color=ACCENT if ours else TEXT_MUTED,
            fontweight="bold" if ours else "normal",
        )

    # Explicit margins give any rotated x-labels guaranteed room. The
    # bbox_inches="tight" below then trims outer whitespace while keeping
    # the title, ticks, and rotated labels visible.
    fig.subplots_adjust(
        left=0.14,
        right=0.96,
        top=0.88,
        bottom=(0.38 if rotation >= 35 else 0.30) if rotate else 0.18,
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, format="svg", bbox_inches="tight", pad_inches=0.25,
                facecolor=BG, transparent=False)
    plt.close(fig)
    print(f"  Saved → {out_path}")


# =============================================================================
# MIKASA-ROBO BENCHMARK — grouped bar chart, 5 tasks × 6 methods
# Replots exp10_mikasa.jpg with the site's warm palette
# =============================================================================
MIKASA_TASKS   = ["ShellGameTouch", "InterceptMedium", "RememberColor3",
                  "RememberColor5", "RememberColor9"]
MIKASA_METHODS = ["Octo-small", "OpenVLA", "SpatialVLA", "π0", "MemoryVLA",
                  "Ours"]

# values[method][task]
MIKASA_VALUES = [
    [46, 39, 45, 17, 11],   # Octo-small
    [47, 14, 59, 16,  6],   # OpenVLA
    [23, 27, 27, 17, 11],   # SpatialVLA
    [33, 42, 35, 22, 15],   # π0
    [88, 24, 44, 30, 20],   # MemoryVLA
    [98, 83, 80, 61, 17],   # GMP (ours)
]

# Warm-family shades for the 5 baselines, terracotta ACCENT reserved for ours
MIKASA_COLORS = ["#d8c8ad", "#c7b391", "#b29a73", "#9a7f56", "#7a5f3d", ACCENT]


def plot_mikasa(out_path: str) -> None:
    n_tasks   = len(MIKASA_TASKS)
    n_methods = len(MIKASA_METHODS)

    fig, ax = plt.subplots(figsize=(11.5, 2.7))
    fig.set_facecolor(BG)
    ax.set_facecolor(BG)

    task_positions = np.arange(n_tasks)
    bar_width      = 0.13
    offsets = (np.arange(n_methods) - (n_methods - 1) / 2) * bar_width * 1.04

    for i, method in enumerate(MIKASA_METHODS):
        color   = MIKASA_COLORS[i]
        is_ours = (method == "Ours")
        bars = ax.bar(
            task_positions + offsets[i],
            MIKASA_VALUES[i],
            bar_width,
            color=color,
            zorder=3,
            linewidth=0,
            label=method,
        )
        for bar, val in zip(bars, MIKASA_VALUES[i]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.4,
                str(val),
                ha="center", va="bottom",
                fontsize=11,
                color=ACCENT if is_ours else TEXT_MUTED,
                fontweight="bold" if is_ours else "normal",
            )

    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=14, color=TEXT_MUTED)

    ax.set_xticks(task_positions)
    ax.set_xticklabels(MIKASA_TASKS, fontsize=14.5, color=TEXT)

    ax.set_ylabel("Success Rate (%)", fontsize=13, color=TEXT_MUTED, labelpad=5)

    ax.yaxis.grid(True, color=BORDER, linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["bottom"].set_linewidth(0.6)
    ax.tick_params(axis="both", length=0, pad=4)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=6,
        frameon=False,
        fontsize=10.5,
        labelcolor=TEXT,
        handlelength=1.4,
        handleheight=1.1,
        columnspacing=1.6,
    )

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, format="svg", bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved → {out_path}")


# ── Run ───────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
charts_dir = os.path.abspath(os.path.join(script_dir, "..", "assets", "charts"))

for task_rel, entries in TASKS.items():
    out = os.path.join(charts_dir, task_rel, "success_rate.svg")
    plot_task(out, entries)

plot_mikasa(os.path.join(charts_dir, "mikasa_benchmark.svg"))

print("Done.")
