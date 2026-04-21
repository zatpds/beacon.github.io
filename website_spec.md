# Gated Memory Policy website spec

Single page research paper site. Plain HTML, CSS, JS. No build step.

## Quick start

```bash
cd /Users/jinyun/Documents/mem_website
python3 -m http.server 8080
# visit http://localhost:8080
```

## File map

```text
mem_website/
  index.html          all page content
  style.css           all visual styling
  main.js             tab switching, video preload, section reveal, TOC, BibTeX
  website_spec.md     this file
  scripts/            python chart generators (plot_success_rate.py, plot_robomimic.py)
  paper/              dated paper PDFs (latest one is linked from the "Paper" button)
  assets/
    favicon.png
    images/           team headshots, architecture/gating PNGs, hf-logo.svg, overlays
    charts/           SVG bar charts (output of scripts/plot_*.py)
    videos/           teaser + cross_trial/ + in_trial/ + attention_vis_*.mp4
```

## Design system

All tokens live in `style.css` under `:root`. Changing them propagates site wide.

### Palette (warm cream, academic press feel)

| Token          | Value                     | Role                                      |
| -------------- | ------------------------- | ----------------------------------------- |
| `--bg`         | `#faf7f0`                 | main page background                      |
| `--bg-alt`     | `#f2ece0`                 | footer background                         |
| `--surface`    | `#fdfbf6`                 | elevated card surface                     |
| `--surface-hi` | `#fffefa`                 | hover surface                             |
| `--text`       | `#1a1612`                 | body and heading text                     |
| `--text-soft`  | `#3a3328`                 | secondary text                            |
| `--text-muted` | `#78695a`                 | captions, eyebrows, inactive tab labels   |
| `--text-faint` | `#b2a390`                 | very low emphasis                         |
| `--accent`     | `#b5552a`                 | active tab, link, corresponding author †  |
| `--accent-rgb` | `181, 85, 42`             | rgba() form of accent                     |
| `--border`     | `rgba(60, 45, 25, 0.13)`  | default divider                           |
| `--hairline`   | `rgba(60, 45, 25, 0.06)`  | faint rule                                |

### Typography

- Body and UI: `Inter` via Google Fonts. Weights 300 to 800.
- Accent / code: `JetBrains Mono` (tab numerics, etc).
- OpenType features enabled: `ss01`, `cv11`, `cv05`, `kern`, `liga`, `calt`.
- Headings use the same Inter stack with weight 600 and tighter line height.
- Body base size: `17px`, line height `1.7`.

### Layout

- Max content width: `960px`, centered via `margin: 0 auto`.
- Section horizontal padding: `24px` (token `--pad-x`), collapses to single column at `max-width: 640px`.
- Top level sections (`#cross-trial`, `#in-trial`, `#method`, `#attention`, `#benchmark`, `#faq`, `#team`) have `padding-top: 140px; padding-bottom: 140px` to give chapter breaks. Free scroll, no snap.
- Only network dependency: Google Fonts.

### Motion

- Scrolling uses the browser default. No snap, no hijacking.
- Each top level section slides up and fades in when it enters the viewport (see `.section-reveal` in `style.css`). `prefers-reduced-motion` disables it.
- Tab underline slides in via `transform: scaleX`.
- Link hover shows a sliding arrow indicator.

## HTML contracts used by JS

`main.js` reads the following DOM shapes. Keep them intact when editing content.

### Tab system

```html
<div class="tab-bar" role="tablist" data-tabgroup="GROUP">
  <button class="tab-btn active" data-tab="VALUE" role="tab">Label</button>
  <button class="tab-btn"        data-tab="VALUE2" role="tab">Label 2</button>
</div>

<div class="tab-panel active" data-tabgroup="GROUP" data-config="VALUE">
  ... videos, text, etc ...
</div>
<div class="tab-panel" data-tabgroup="GROUP" data-config="VALUE2">
  ...
</div>
```

The `data-tab` on a button must match the `data-config` on exactly one panel in the same `data-tabgroup`. `data-tabgroup` must be unique per subsection.

Tab groups currently in use:

| tabgroup          | Section                                | Axis                  | tabs |
| ----------------- | -------------------------------------- | --------------------- | ---- |
| `pushing`         | Cross Trial Pushing                    | friction coefficient  | 6    |
| `casting`         | Cross Trial Casting                    | friction regime       | 2    |
| `flinging`        | Cross Trial Flinging                   | cloth mass            | 7    |
| `place-back-real` | In Trial Continuous Place Back (Real)  | object location       | 5    |
| `match-color`     | In Trial Match Color                   | target location       | 4    |
| `place-back`      | In Trial Place Back (Sim)              | object location       | 4    |
| `attn-vis`        | Attention Visualization                | task                  | 2    |

### Videos

- All 85 comparison clips: `<video autoplay loop muted playsinline preload="none">`, no `controls`.
- The 2 attention visualization clips keep `controls` so the reader can scrub.
- Every `<video>` lives inside a `<figure>`. The global rule `figure video { width: 100%; border-radius: 6px; display: block }` handles sizing; no inline style needed.

### Sticky TOC

```html
<nav id="toc-nav">
  <div class="toc-inner">
    <a class="toc-link" href="#section-id">Label</a>
    ...
  </div>
</nav>
```

JS adds `.visible` to `#toc-nav` after the hero leaves view, and `.active` to the link whose section is currently in the upper portion of the viewport.

### BibTeX copy

```html
<pre><code id="bibtex-content">...</code></pre>
<button class="copy-btn" onclick="copyBibtex(this)">Copy BibTeX</button>
```

## JS architecture

`main.js` is organised into six independent blocks.

### 1. Tab switching

Generic handler attached per `.tab-bar`. On click it removes `.active` from sibling buttons and panels in the same tabgroup, activates the clicked one, and calls `video.load()` on videos inside the newly shown panel so autoplay resumes after `display:none`.

### 2. Video preload + playback (three layer)

Goal: user never sees a buffering spinner; Chrome's decoder pool is never flooded.

- **Intent layer**. Videos are sorted in DOM order. A frontier advances so that `AHEAD` (15) videos ahead of the near viewport edge are queued. Visibility and tab click events can promote videos to the front of the queue.
- **Prefetch layer**. A FIFO queue drained during browser idle time (`requestIdleCallback` with a 1500ms timeout fallback). Concurrency capped at `MAX_INFLIGHT` (4) with `canplaythrough` freeing a slot. `fetchPriority` is `high` for videos laid out within 1.2x the viewport height at boot ("hot start") and `low` for everything else, so the first screen never waits behind below-fold prefetches.
- **Playback layer**. `IntersectionObserver` at `threshold: 0.25` plays videos that are visible and pauses them the moment they leave. Scrolling back to a previously seen video auto-resumes it.

Save-Data and 2G connections downshift to `AHEAD=2, MAX_INFLIGHT=2`.

### 3. YouTube facade

The hero teaser renders as a thumbnail (`i.ytimg.com/vi/<id>/maxresdefault.jpg`) plus a play button. The real YouTube iframe is only inserted on click/Enter/Space. Saves ~500KB of YouTube JS/CSS on first paint and keeps bandwidth available for comparison videos.

### 4. Section slide in

One `IntersectionObserver` watches each top level section (`#cross-trial`, `#in-trial`, `#method`, `#attention`, `#benchmark`, `#faq`, `#team`). When a section enters the viewport (`threshold: 0.04`), `.is-visible` is added and the whole section slides up 90px and fades in over 0.9s. Fires once per section. Sections already in the viewport on load are not animated.

### 5. Sticky TOC nav

Visible from the first content section through to just before the footer. Uses a scroll listener (passive) plus an `IntersectionObserver` (rootMargin `-15% 0 -75% 0`) to highlight the current section.

### 6. BibTeX copy

Clipboard API with an `execCommand` fallback. Button shows "Copied!" for 2 seconds.

## Section inventory

| id             | Title                   | Notes                                      |
| -------------- | ----------------------- | ------------------------------------------ |
| `#hero-title`  | Hero card               | Paper title, authors, link buttons         |
| `#intro-split` | Teaser video + abstract | YouTube iframe + abstract paragraphs       |
| `#cross-trial` | Cross Trial Memory      | Pushing, Casting, Flinging subsections     |
| `#in-trial`    | In Trial Memory         | Place Back (Real), Match Color, Place Back |
| `#method`      | Method                  | Architecture + Gating Mechanism (zigzag)   |
| `#attention`   | Attention Visualization | Tabs for cube pushing and match color      |
| `#benchmark`   | Benchmark Performance   | RoboMimic + Mikasa Robo stacked            |
| `#faq`         | Questions & Answers     | `<details>` accordion                      |
| `#team`        | Team                    | Author grid                                |
| `#footer`      | Footer                  | Citation, BibTeX, acknowledgements         |

## Maintenance how-tos

### Add a new tab within a subsection

1. Drop the three mp4 files under `assets/videos/.../[new_config]/`.
2. Add a new `<button class="tab-btn" data-tab="new_config">` to the tab bar.
3. Add a new `<div class="tab-panel" data-tabgroup="X" data-config="new_config">` with the video grid.

### Change the accent color

Edit `--accent` and `--accent-rgb` under `:root` in `style.css`. Tabs, links, author marker, focus ring all update together. Rerun the chart generators (`scripts/plot_*.py`) so chart SVGs match.

### Regenerate charts

```bash
cd /Users/jinyun/Documents/mem_website/scripts
python plot_success_rate.py   # per task success rate bars + mikasa benchmark
python plot_robomimic.py      # robomimic grouped bar chart
```

Each script uses the site palette tokens defined at the top of the file.

### Hide a section

Wrap the section in `<!--` ... `-->` or remove it. Also remove its `.toc-link` entry in `#toc-nav`. Nothing else is wired.

### Add a new top level section

1. Add `<section id="new-section">...</section>` in the DOM order you want.
2. Add `.toc-link` to `#toc-nav`.
3. If it should get the chapter break padding, append `#new-section` to the selector list in the MAJOR SECTIONS block of `style.css`.
