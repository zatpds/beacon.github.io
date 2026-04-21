"""
make_in_the_wild_grid.py
Tiles N iPhone trial videos (HEVC/HLG) into a single wide SDR grid for the
In-the-Wild section. Two stage pipeline:

    Stage 1 (per input, cached):
        HEVC HLG -> Hable tonemap -> bt709 SDR -> scale to cell
                 -> clone last frame to DUR -> H.264 CRF 17 mezzanine
                 (visually lossless at this size)

    Stage 2 (single):
        xstack the 40 mezzanines into COLS x ROWS grid
        -> H.264 CRF 23, faststart, no audio

Mezzanines live in scripts/.mezz/ and are reused on subsequent runs (much
faster iteration when tweaking the layout or CRF). Delete that directory
to force a rebuild, or touch a source .MOV to invalidate just that cell.

Usage:
    cd /path/to/mem_website/scripts
    python make_in_the_wild_grid.py
    # override any knob via env var, e.g.:
    CELL_W=320 CELL_H=180 CRF=20 python make_in_the_wild_grid.py
"""

import os
import subprocess
import sys

# ── Config (override any via env var) ─────────────────────────────────────────
IN_DIR   = os.path.expanduser(os.environ.get("IN_DIR",  "~/Downloads/in-the-wild"))
OUT_REL  = os.environ.get("OUT_REL",
                          "assets/videos/in_trial/place_back_real/in_the_wild_ours.mp4")
COLS     = int(os.environ.get("COLS",    8))
ROWS     = int(os.environ.get("ROWS",    5))
CELL_W   = int(os.environ.get("CELL_W",  240))   # grid width  = COLS * CELL_W
CELL_H   = int(os.environ.get("CELL_H",  136))   # grid height = ROWS * CELL_H (must be even)
DUR      = float(os.environ.get("DUR",   15))    # seconds; short clips freeze to fill
FPS      = int(os.environ.get("FPS",     30))
CRF      = int(os.environ.get("CRF",     23))    # final grid quality
MEZZ_CRF = int(os.environ.get("MEZZ_CRF", 17))   # mezzanine (visually lossless at cell size)
PRESET   = os.environ.get("PRESET",      "medium")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT  = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MEZZ_DIR   = os.path.join(SCRIPT_DIR, ".mezz")
OUT_PATH   = os.path.join(REPO_ROOT, OUT_REL)


def probe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", path],
        text=True,
    ).strip()
    return float(out)


def mezz_path(src: str) -> str:
    stem = os.path.splitext(os.path.basename(src))[0]
    tag  = f"{CELL_W}x{CELL_H}_dur{int(DUR)}_fps{FPS}"
    return os.path.join(MEZZ_DIR, f"{stem}__{tag}.mp4")


def needs_build(src: str, dst: str) -> bool:
    return not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst)


def build_mezzanine(src: str, dst: str) -> None:
    """Stage 1: one input -> one 240x136 SDR mezzanine. Short clips freeze
    on their last frame to fill DUR; longer clips are trimmed at DUR."""
    vf = (
        "zscale=t=linear:npl=100,format=gbrpf32le,"
        "zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
        "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
        f"scale={CELL_W}:{CELL_H}:flags=bicubic,setsar=1,fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration={DUR},trim=0:{DUR},setpts=PTS-STARTPTS"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", src, "-vf", vf, "-an",
         "-c:v", "libx264", "-crf", str(MEZZ_CRF), "-preset", PRESET,
         "-pix_fmt", "yuv420p", dst],
        check=True,
    )


def build_grid(mezzanines: list[str]) -> None:
    """Stage 2: xstack N mezzanines into the final grid."""
    if (CELL_H * ROWS) % 2 or (CELL_W * COLS) % 2:
        sys.exit(f"Grid {CELL_W*COLS}x{CELL_H*ROWS} has odd dimension; libx264 needs even.")

    layout = "|".join(f"{c*CELL_W}_{r*CELL_H}" for r in range(ROWS) for c in range(COLS))
    fc = (
        "".join(f"[{i}:v]" for i in range(len(mezzanines)))
        + f"xstack=inputs={len(mezzanines)}:layout={layout}[out]"
    )
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    # -tune fastdecode:   lower decoder cost in the browser, smoother playback
    # -g 30:              keyframe every second so native <video loop> can
    #                     restart from frame 0 without a multi-frame IDR wait
    # -profile:v main:    widely GPU-accelerated on every mainstream browser
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y"]
        + [arg for m in mezzanines for arg in ("-i", m)]
        + ["-filter_complex", fc, "-map", "[out]",
           "-c:v", "libx264", "-crf", str(CRF), "-preset", PRESET,
           "-tune", "fastdecode", "-profile:v", "main", "-g", str(FPS),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
           OUT_PATH],
        check=True,
    )


if __name__ == "__main__":
    needed = COLS * ROWS
    files  = sorted(os.path.join(IN_DIR, f) for f in os.listdir(IN_DIR)
                    if f.lower().endswith((".mov", ".mp4", ".m4v")))
    if len(files) < needed:
        sys.exit(f"Need {needed} clips in {IN_DIR}, found {len(files)}.")
    files = files[:needed]

    os.makedirs(MEZZ_DIR, exist_ok=True)
    mezzanines = []
    for i, src in enumerate(files, 1):
        dst = mezz_path(src)
        if needs_build(src, dst):
            print(f"  [{i:>2}/{needed}] mezzanine  {os.path.basename(src)}")
            build_mezzanine(src, dst)
        else:
            print(f"  [{i:>2}/{needed}] cached     {os.path.basename(src)}")
        mezzanines.append(dst)

    print(f"Stacking {needed} cells -> {COLS*CELL_W}x{ROWS*CELL_H} grid, CRF {CRF}")
    build_grid(mezzanines)
    print(f"Wrote {OUT_PATH}")
