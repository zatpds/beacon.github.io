# Research Project Release Website — Implementation Specification

*Last updated to reflect current implementation.*

`To launch on local run cd /Users/jinyun/Documents/mem_website && python3 -m http.server 8080. Then visit http://localhost:8080.`
---

## File Structure

```text
mem_website/
├── index.html          — all page content (pure HTML, no inline style/script)
├── style.css           — all visual styling
├── main.js             — tab switching + BibTeX copy (vanilla JS, ~80 lines)
└── assets/
    ├── videos/
    │   ├── teaser.mp4
    │   ├── attention_vis_cube_pushing.mp4
    │   ├── cross_trial/
    │   │   ├── pushing/
    │   │   │   ├── friction_0.015/ {ours.mp4, long_hist_dp.mp4, no_hist_dp.mp4}
    │   │   │   ├── friction_0.03/  {…}
    │   │   │   ├── friction_0.06/  {…}
    │   │   │   ├── friction_0.09/  {…}
    │   │   │   ├── friction_0.12/  {…}
    │   │   │   ├── friction_0.16/  {…}
    │   │   │   └── friction_0.2/   {…}
    │   │   ├── casting/
    │   │   │   ├── high_friction/  {ours.mp4, long_hist_dp.mp4, no_hist_dp.mp4}
    │   │   │   └── low_friction/   {…}
    │   │   └── flinging/
    │   │       ├── mass_low/       {…}
    │   │       ├── mass_mid_low/   {…}
    │   │       ├── mass_mid_high/  {…}
    │   │       └── mass_high/      {…}
    │   └── in_trial/
    │       ├── cup/
    │       │   ├── loc_A/ {ours.mp4, long_hist_dp.mp4, no_hist_dp.mp4}
    │       │   ├── loc_B/ {…}
    │       │   ├── loc_C/ {…}
    │       │   └── in_the_wild_ours.mp4
    │       ├── match_color/
    │       │   ├── attention_vis.mp4
    │       │   ├── loc_A/ {ours.mp4, long_hist_dp.mp4, no_hist_dp.mp4}
    │       │   ├── loc_B/ {…}
    │       │   ├── loc_C/ {…}
    │       │   └── loc_D/ {…}
    │       └── place_back/
    │           ├── loc_A/ {…}
    │           ├── loc_B/ {…}
    │           ├── loc_C/ {…}
    │           └── loc_D/ {…}
    ├── images/
    │   ├── architecture.png
    │   ├── gating_training.png
    │   └── cup_overlay/
    │       ├── loc_A/initial_pos.png
    │       ├── loc_B/initial_pos.png
    │       └── loc_C/initial_pos.png
    └── charts/
        ├── robomimic_bar_chart.png
        └── cross_trial/casting/
            ├── high_friction_bar_chart.png
            └── low_friction_bar_chart.png
```

---

## Design System

### Color Palette

| Token | Value | Usage |
| --- | --- | --- |
| `--bg` | `#f9f8f5` | Page background |
| `--bg-alt` | `#f0ede6` | Hero title card, abstract strip, footer |
| `--text` | `#1a1a1a` | Body and heading text |
| `--text-muted` | `#6b6560` | Captions, secondary text, inactive tabs |
| `--accent` | `#c97d3b` | Section labels, "Ours" column headers, config row labels |
| `--border` | `#ddd8cf` | Dividers, placeholder borders, tab bar underline |
| `--tab-active` | `#2d4a6e` | Active tab text + underline indicator (deep slate-blue) |

**Rationale:** `--accent` (warm ochre) is used sparingly for scientific emphasis — section taxonomy labels and the "Ours" column to visually distinguish our method. `--tab-active` is intentionally a cool deep navy to contrast with the warm background without looking like a product brand color. The overall palette reads as warm-academic, similar to aged paper.

### Typography

- **Headings** (`h1`–`h4`): `Playfair Display`, serif. `h1` is italic weight-400 for the paper title; `h2`–`h3` are weight-600 upright.
- **Body / UI**: `DM Sans`, sans-serif, weight 300/400/500.
- **Font sizes**:
  - `h1` (paper title): `clamp(2rem, 5vw, 3.4rem)`, italic
  - `h2` (section headings): `clamp(1.5rem, 3vw, 2rem)`
  - `h3` (subsection headings): `1.35rem`
  - Body: `17px` / `1.75` line-height
  - Captions (`figcaption`): `0.845rem`, italic, `--text-muted`
  - Section labels: `0.72rem`, `0.14em` letter-spacing, uppercase, `--accent`
  - Tab buttons: `0.825rem`
  - Column headers: `0.75rem`, `--text-muted` (or `--accent` for "Ours")

### Spacing

- **Max content width**: `960px`, centered via `margin: 0 auto`
- **Section padding**: `80px` top/bottom, `24px` horizontal (collapses to `56px` on mobile)
- **Section dividers**: `1px solid var(--border)` between consecutive `<section>` elements
- **Video grid gap**: `14px`
- **Result row margin**: `44px` bottom

---

## Global Layout Rules

- **Single-file HTML** with external `style.css` and `main.js`. No frameworks, no build step.
- All `<section>` tags: `width: 100%; max-width: 960px; margin: 0 auto;` — guarantees centering.
- No client-side routing. Page is top-to-bottom linear scroll.
- Only external network dependency: Google Fonts (`Playfair Display` + `DM Sans`) via `<link>` in `<head>`.
- **Responsive**: at `≤ 640px`, all `.three-col` and `.four-col` grids collapse to single column.

---

## Placeholder Convention

When an asset is missing, render:

```html
<div class="placeholder-media">path/to/asset.mp4</div>
```

- White background (`#ffffff`), subtle `1.5px` border (`#e8e4de`)
- `aspect-ratio: 16/9` by default; add class `square` for `1/1`
- Centered play icon via CSS `::before` pseudo-element (SVG data URI)
- Chart placeholders: `.placeholder-media.square`
- Hero video: overridden to dark background (`#181818`), no border, larger icon

**To swap in a real asset:**

```html
<!-- video -->
<video autoplay loop muted playsinline>
  <source src="assets/videos/…" type="video/mp4">
</video>

<!-- image / chart -->
<img src="assets/images/…" alt="description">
```

---

## Tab System

### Design

All config-level selectors use a **horizontal underline tab bar** — no filled pill buttons.

- **Inactive**: muted text (`--text-muted`), no border
- **Hover**: full text color (`--text`)
- **Active**: deep slate-blue text + `2px` bottom border (`--tab-active: #2d4a6e`)
- Tab bar has `border-bottom: 1px solid var(--border)` and `overflow-x: auto; scrollbar-width: none` for overflow cases (e.g. 7-tab pushing row)
- Active tab sits on top of bar border via `margin-bottom: -1px`

### HTML Contract

```html
<!-- Tab bar -->
<div class="tab-bar" role="tablist" data-tabgroup="GROUP_NAME">
  <button class="tab-btn active" data-tab="CONFIG_VALUE" role="tab">Label</button>
  <button class="tab-btn"        data-tab="CONFIG_VALUE" role="tab">Label</button>
</div>

<!-- Tab panels (one per config value) -->
<div class="tab-panel active" data-tabgroup="GROUP_NAME" data-config="CONFIG_VALUE">
  <!-- video grid content -->
</div>
<div class="tab-panel" data-tabgroup="GROUP_NAME" data-config="CONFIG_VALUE">
  …
</div>
```

**Key:** `button[data-tab]` value must exactly match the corresponding `div[data-config]` value. `data-tabgroup` must be unique per subsection.

### Tab Groups in Use

| `data-tabgroup` | Section | Config axis | # tabs |
| --- | --- | --- | --- |
| `pushing` | § 4A Cross-Trial Pushing | Friction coefficient | 7 |
| `casting` | § 4B Cross-Trial Casting | Friction regime | 2 |
| `flinging` | § 4C Cross-Trial Flinging | Cloth mass | 4 |
| `cup` | § 5A In-Trial Cup | Object location | 3 |
| `match-color` | § 5B In-Trial Match Color | Target location | 4 |
| `place-back` | § 5C In-Trial Place Back | Object location | 4 |

### JS Behavior (`main.js`)

On tab click:

1. Remove `.active` from all `.tab-btn` in the same `data-tabgroup`
2. Remove `.active` from all `.tab-panel` with the same `data-tabgroup`
3. Add `.active` to the clicked button
4. Add `.active` to `.tab-panel[data-tabgroup][data-config]` matching the clicked `data-tab`
5. Call `video.load()` + `video.play()` on any `<video>` inside the newly active panel (restores autoplay after `display:none`)

---

## Section-by-Section Specification

### Hero — Title Card (`#hero-title`)

- Full-width, `background: var(--bg-alt)`
- Paper title: `Playfair Display`, italic, large, centered, `max-width: 820px`
- Authors line + Institution line below, `--text-muted`
- Three icon+text link buttons (Paper, Code, Video) with inline SVG icons
  - Style: outlined pill with `1.5px` border, hover fills to `--text` background
  - Icons: document (Paper), GitHub octocat (Code), YouTube play (Video)

### Hero — Teaser Video (`#hero-video`)

- Full viewport width, `min-height: 56.25vw` (16:9), `max-height: 90vh`
- Dark background `#0f0f0f`, video covers the strip with `object-fit: cover`
- No controls shown. Attributes: `autoplay loop muted playsinline`
- Asset: `assets/videos/teaser.mp4`

### Abstract (`#abstract`)

- `background: var(--bg-alt)`, centered `<p>`, `max-width: 700px`
- `font-size: 1.025rem`, `line-height: 1.85`
- Separated from sections below by `border-bottom: 1px solid var(--border)`

### § 2 — Model Architecture (`#architecture`)

- Section label: "Method"
- Full-width figure, `max-width: 860px`, centered via `.fig-centered`
- Asset: `assets/images/architecture.png`
- Explanatory paragraph below (`.body-text`)

### § 3 — What Is the Policy Attending To? (`#attention`)

- Section label: "Interpretability"
- Intro paragraph → centered video figure (`max-width: 720px`) → follow-up paragraph
- Asset: `assets/videos/attention_vis_cube_pushing.mp4`

### § 4 — Cross-Trial Memory (`#cross-trial`)

All three subsections use the tab system. Each `.tab-panel` contains:

1. `.row-caption.before` — context sentence
2. `.video-grid.three-col` (or `.four-col` for Casting) — one `.video-col` per policy
3. `.row-caption.after` — observation sentence

**4A — Pushing** (`#cross-trial-pushing`): 7 tabs, friction axis, labels `µ = 0.015` … `µ = 0.2`. Three-column grid.

**4B — Casting** (`#cross-trial-casting`): 2 tabs (`High Friction` / `Low Friction`). Four-column grid: 3 videos + 1 bar chart (`.placeholder-media.square`). Bar chart assets: `assets/charts/cross_trial/casting/[level]_bar_chart.png`.

**4C — Flinging** (`#cross-trial-flinging`): 4 tabs (`Low` / `Mid-Low` / `Mid-High` / `High`), cloth mass axis. Three-column grid.

### § 5 — In-Trial Memory (`#in-trial`)

**5A — Cup** (`#in-trial-cup`): 3 tabs (Location A/B/C). Each tab panel additionally includes a `<details class="overlay-details">` accordion below the video grid. Opening the accordion reveals a three-column grid of `.placeholder-media.square` initial position images. Below all tabs: a permanently visible "In-the-Wild" block with a single centered video (`max-width: 640px`).

- Initial position images: `assets/images/cup_overlay/[loc_X]/initial_pos.png`
- In-the-wild video: `assets/videos/in_trial/cup/in_the_wild_ours.mp4`

**5B — Match Color** (`#in-trial-match-color`): Two independent visual blocks:

1. **Attention visualization block** (`.attention-block`) — always visible, not affected by tab selection. Video `assets/videos/in_trial/match_color/attention_vis.mp4`. Has a small-caps `vis-label` above it.
2. **Location tab selector** — 4 tabs (Location A/B/C/D), standard three-column video grid per panel.

**5C — Place Back** (`#in-trial-place-back`): 4 tabs (Location A/B/C/D). Standard three-column grid per panel.

### § 6 — How to Train the Gating Mechanism (`#gating-training`)

- Section label: "Method"
- Full-width figure (`max-width: 860px`). Asset: `assets/images/gating_training.png`
- Explanatory paragraph below

### § 7 — Robomimic Benchmark Results (`#robomimic`)

- Section label: "Quantitative Results"
- Centered figure, `max-width: 720px`. Asset: `assets/charts/robomimic_bar_chart.png`
- Short explanation paragraph below

### Footer (`#footer`)

- `background: var(--bg-alt)`, `max-width: 960px` container
- ACM/IEEE citation line
- BibTeX block: `<pre><code id="bibtex-content">` + `Copy BibTeX` button (Clipboard API + execCommand fallback, 2 s feedback, class `.copied` on success)
- Acknowledgements line
- Copyright line

---

## Component Reference

### `.video-grid`

```css
display: grid; width: 100%; gap: 14px;
/* .three-col → 1fr 1fr 1fr */
/* .four-col  → 1fr 1fr 1fr 1fr */
```

Collapses to single column at `≤ 640px`.

### `.video-col`

Flex column containing: `.col-header` (label) → `<figure>` (video/placeholder + optional figcaption).

`.col-header.ours` uses `--accent` color and `font-weight: 600` to highlight our method.

### `.tab-panel` / `.tab-btn`

`display: none` / `display: block` toggled by `main.js`. Initial active state set directly in HTML via `.active` class.

### `.overlay-details` (Cup § 5A)

Native `<details><summary>` element — zero JS, browser-native accordion. Summary has a CSS `▸` arrow that rotates 90° when open. Opens a `.three-col` grid of square image placeholders.

### `.attention-block` (Match Color § 5B)

Always-visible figure block. `border-bottom: 1px solid var(--border)` separates it from the tab bar below. Max-width `720px`, centered.

### `.in-the-wild-block` (Cup § 5A)

Full-width sub-block below all cup tabs. `border-top: 1px solid var(--border)`. Centered figure, `max-width: 640px`.

### `.fig-centered`

`max-width: 860px; margin: 0 auto 1.5rem;`. Used for architecture and gating diagrams.

---

## Notes for Future Changes

### Adding a new friction/mass/location level

1. Add an `assets/videos/…/[new_config]/` folder with the three `.mp4` files
2. Add a new `<button class="tab-btn" data-tab="new_config">` to the relevant tab bar
3. Add a new `<div class="tab-panel" data-tabgroup="X" data-config="new_config">` with the video grid

### Changing the active tab color

Edit `--tab-active` in `style.css` (defined in `:root` block, currently `#2d4a6e`).

### Changing the accent color (section labels, "Ours" headers)

Edit `--accent` in `style.css` `:root` (currently `#c97d3b`).

### Replacing any placeholder with a real asset

Swap the `<div class="placeholder-media">` for `<video autoplay loop muted playsinline><source src="…" type="video/mp4"></video>` (or `<img src="…">` for images/charts) inside the same `<figure>` element.

### Collapsing a subsection into a single-select dropdown (future UX)

The tab bar `.tab-btn`/`.tab-panel` pattern maps directly onto a `<select>` + JS `change` handler. Replace the `.tab-bar` with `<select data-tabgroup="X">` and wire `option[value]` → panel `data-config`. No HTML restructuring needed.
