"""
plot_success_rate.py
Generates one success-rate SVG bar chart per task.
Styled to match the Gated Memory Policy website palette.

Usage:
    cd /path/to/mem_website/assets/charts
    python plot_success_rate.py

Output (relative to this script's directory):
    cross_trial/pushing/success_rate.svg
    cross_trial/casting/success_rate.svg
    cross_trial/flinging/success_rate.svg
    in_trial/cup/success_rate.svg
    in_trial/match_color/success_rate.svg
    in_trial/place_back/success_rate.svg
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Site palette ──────────────────────────────────────────────────────────────
BG         = "#FFF4EA"
TEXT       = "#2b2521"
TEXT_MUTED = "#6e6358"
ACCENT     = "#BF4646"   # highlight color for "Ours"
NEUTRAL    = "#C4B5A5"   # baseline bars
BORDER     = "#d8c8b5"

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
        {"label": "Ours\n(GMP)", "value": 97,   "err": 0, "ours": True },
    ],
    "cross_trial/casting": [
        {"label": "nh-DP",       "value": 5,    "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 20,   "err": 0, "ours": False},
        {"label": "Ours\n(GMP)", "value": 95,   "err": 0, "ours": True },
    ],
    "cross_trial/flinging": [
        {"label": "nh-DP",       "value": 54,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 54,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 54,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 65,   "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 69,   "err": 0, "ours": False},
        {"label": "Ours\n(GMP)", "value": 81,   "err": 0, "ours": True },
    ],
    "in_trial/cup": [
        {"label": "nh-DP",       "value": 10,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 62.5, "err": 0, "ours": False},
        {"label": "Ours\n(GMP)", "value": 85,   "err": 0, "ours": True },
    ],
    "in_trial/match_color": [
        {"label": "nh-DP",       "value": 16,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 35,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 35,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 100,  "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 100,  "err": 0, "ours": False},
        {"label": "Ours\n(GMP)", "value": 100,  "err": 0, "ours": True },
    ],
    "in_trial/place_back": [
        {"label": "nh-DP",       "value": 18,   "err": 0, "ours": False},
        {"label": "mh-DP",       "value": 64,   "err": 0, "ours": False},
        {"label": "mh-PTP",      "value": 56,   "err": 0, "ours": False},
        {"label": "lh-DP",       "value": 100,  "err": 0, "ours": False},
        {"label": "lh-PTP",      "value": 100,  "err": 0, "ours": False},
        {"label": "Ours\n(GMP)", "value": 98,   "err": 0, "ours": True },
    ],
}

# ── Global font settings ──────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":        "sans-serif",
    "font.sans-serif":    ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
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
    fig_w  = 6.0   # fixed 9:5 landscape ratio for all charts
    fig_h  = 3.5

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

    ax.set_ylim(0, 118)
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(["0", "50", "100"], fontsize=14, color=TEXT_MUTED)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=14.5, color=TEXT, linespacing=1.3)
    for tick, ours in zip(ax.get_xticklabels(), is_ours):
        if ours:
            tick.set_color(ACCENT)
            tick.set_fontweight("bold")

    ax.set_ylabel("Success Rate (%)", fontsize=13, color=TEXT_MUTED, labelpad=5)

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
            fontsize=14,
            color=ACCENT if ours else TEXT_MUTED,
            fontweight="bold" if ours else "normal",
        )

    plt.tight_layout(pad=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, format="svg", bbox_inches="tight",
                facecolor=BG, transparent=False)
    plt.close(fig)
    print(f"  Saved → {out_path}")


# ── Run ───────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))

for task_rel, entries in TASKS.items():
    out = os.path.join(script_dir, task_rel, "success_rate.svg")
    plot_task(out, entries)

print("Done.")
