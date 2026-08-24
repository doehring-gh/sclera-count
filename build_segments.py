#!/usr/bin/env python3
"""
build_segments.py -- cut confocal fields into per-square segments and emit the
static assets the counting app (docs/index.html) consumes.

Run with /usr/bin/python3 (bare python3 is the broken anaconda one).

    /usr/bin/python3 build_segments.py --z-levels 5,9,13,17 --squares-per-field 16

What it does
------------
Each z-slice of each stack becomes a "field", divided into the same A-H x 1-8
grid used by COUNT_field_*_grid.png, so segment ids stay comparable with the
counts Maryam and Louise returned. For every grid square it writes co-registered
tile images, one per channel view, which the app stacks as toggleable layers --
so a marker placed while looking at Hoechst stays put when the counter flips to
EthD-1 to decide live vs dead.

Depth
-----
Stacks are z00..z19 at 5.263 um per slice, about 100 um of tissue. --z-levels
samples several depths from every stack, which turns depth into a factor you can
test rather than a constant nobody chose deliberately (the original five fields
sat at z05-z09).

The same grid square at two depths is the same x,y location, so depth can be
compared within location rather than across fields. To keep that comparison
clean, block assignment guarantees **no counter ever sees the same location at
two depths** -- otherwise they would be recognising a square they have already
counted rather than counting it.

Channels
--------
Per the fixed convention in czi_export.py:
    R = ethidium homodimer-1 (dead)
    G = calcein (live)               [Calcein/EthD scheme]
    B = Hoechst 33342 (all nuclei)   [Hoechst/EthD scheme]
Only Hoechst labels every nucleus, so only that scheme gives a TOTAL to count
dead against. The build prints per-channel statistics and refuses to run if a
field's channel occupancy contradicts the requested scheme.

Display transform
-----------------
Cut levels are pooled over every field in the build, never computed per field.
A per-field stretch would pull a dim slice's noise up into plausible-looking
nuclei -- which matters enormously here, because deep slices ARE dimmer, and a
per-field stretch would hide exactly the depth effect this study is trying to
measure. Levels, percentiles and channel stats all go into the manifest.

Edge cells
----------
Tiles carry a context margin so a counter can see a nucleus straddling the
boundary, but the manifest carries a `count_box` and the app refuses clicks
outside it. Rule: a cell belongs to the square its centre falls in.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

APP_DIR = Path(__file__).resolve().parent
REPO = APP_DIR.parent
CONFOCAL = REPO / "confocal"
GRID_DIR = REPO / "SCLERA_Detection_Analysis" / "manual_count_experiment"

ONLY_SQUARES = set()
COLS = "ABCDEFGH"
ROWS = "12345678"
CH = {"R": 0, "G": 1, "B": 2}
RESAMPLE = {"bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS, "nearest": Image.NEAREST}

Z_UM = 5.263          # z-interval between slices, from calibration.yaml
FIELD_WIDTH_UM = 850.10

# The stacks the manual-count fields came from. Region is resolved by searching
# confocal/<specimen>/*/ (image names are unique within a specimen).
DEFAULT_STACKS = [
    {"specimen": "006", "image": "Image 11"},
    {"specimen": "006", "image": "Image 5"},
    {"specimen": "003", "image": "Image 5"},
    {"specimen": "003", "image": "Image 21"},
    {"specimen": "003", "image": "Image 8"},
]

# The five legacy fields, for --from-grid only (those figures are single-slice).
LEGACY_FIELDS = [
    {"field": 1, "specimen": "006", "image": "Image 11_z09.png"},
    {"field": 2, "specimen": "006", "image": "Image 5_z05.png"},
    {"field": 3, "specimen": "003", "image": "Image 5_z07.png"},
    {"field": 4, "specimen": "003", "image": "Image 21_z07.png"},
    {"field": 5, "specimen": "003", "image": "Image 8_z05.png"},
]

SCHEMES = {
    "hoechst": {
        "desc": "Hoechst 33342 (all nuclei) + ethidium homodimer-1 (dead)",
        "nuclei": "B", "dead": "R", "live": None,
    },
    "calcein": {
        "desc": "calcein (live) + ethidium homodimer-1 (dead)",
        "nuclei": None, "dead": "R", "live": "G",
    },
}

LAYERS_BY_SCHEME = {
    "hoechst": [
        {"key": "merged", "name": "Merged", "name_de": "Überlagert", "hotkey": "q",
         "hint": "blue = Hoechst (every nucleus), red = EthD-1 (dead)",
         "hint_de": "blau = Hoechst (jeder Zellkern), rot = EthD-1 (tot)"},
        {"key": "nuclei", "name": "All nuclei", "name_de": "Alle Zellkerne", "hotkey": "w",
         "hint": "Hoechst. Every spot is a nucleus - this is the TOTAL",
         "hint_de": "Hoechst. Jeder Fleck ist ein Zellkern - das ist die GESAMTZAHL"},
        {"key": "dead", "name": "Dead only", "name_de": "Nur tot", "hotkey": "e",
         "hint": "EthD-1. A spot here on top of a nucleus means that nucleus is DEAD",
         "hint_de": "EthD-1. Ein Fleck hier auf einem Zellkern bedeutet: dieser Kern ist TOT"},
    ],
    "calcein": [
        {"key": "merged", "name": "Merged", "name_de": "Überlagert", "hotkey": "q",
         "hint": "green = calcein (live), red = EthD-1 (dead)",
         "hint_de": "grün = Calcein (lebend), rot = EthD-1 (tot)"},
        {"key": "live", "name": "Live only", "name_de": "Nur lebend", "hotkey": "w",
         "hint": "calcein. Live cells, stained through the cytoplasm",
         "hint_de": "Calcein. Lebende Zellen, im Zytoplasma angefärbt"},
        {"key": "dead", "name": "Dead only", "name_de": "Nur tot", "hotkey": "e",
         "hint": "EthD-1. Dead nuclei", "hint_de": "EthD-1. Tote Zellkerne"},
    ],
}

# Shape carries the meaning; colour only reinforces it. A marker distinguished by
# hue alone fails for a red/green-blind counter and is hard to tell apart on a
# busy greyscale field for everyone else.
_LD = [
    {"key": "live", "name": "Live", "name_de": "Lebend", "colour": "#4da6ff",
     "shape": "circle", "hotkey": "1"},
    {"key": "dead", "name": "Dead", "name_de": "Tot", "colour": "#ff4d6d",
     "shape": "square", "hotkey": "2"},
    {"key": "unsure", "name": "Unsure", "name_de": "Unsicher", "colour": "#f5c518",
     "shape": "triangle", "hotkey": "3"},
]

MODES_BY_SCHEME = {
    "hoechst": {
        "cells": {
            "label": "Nuclei only", "label_de": "Nur Zellkerne",
            "prompt": "Click every nucleus on the Hoechst layer. Do not judge live or dead.",
            "prompt_de": "Klicken Sie jeden Zellkern in der Hoechst-Ansicht an. "
                         "Ohne Beurteilung von lebend oder tot.",
            "default_layer": "nuclei",
            "labels": [{"key": "cell", "name": "Nucleus", "name_de": "Zellkern",
                        "colour": "#f5c518", "shape": "circle", "hotkey": "1"}],
        },
        "livedead": {
            "label": "Live / dead", "label_de": "Lebend / tot",
            "prompt": "Find every nucleus on the greyscale Hoechst view, then switch "
                      "to the dead view to judge each one. A nucleus with EthD-1 on "
                      "it is dead; one without is live.",
            "prompt_de": "Finden Sie jeden Zellkern in der Graustufenansicht "
                         "(Hoechst) und wechseln Sie dann in die Ansicht „Nur tot“, "
                         "um jeden zu beurteilen. Ein Kern mit EthD-1 ist tot, ein "
                         "Kern ohne EthD-1 ist lebend.",
            # Counting happens on a single greyscale channel. Colour-coded overlays
            # are a poor basis for accurate counting, and around one man in twelve
            # cannot use a red/green pair reliably at all (Torsten Bossing, 2026-08-24).
            # The merged view stays available for orientation.
            "default_layer": "nuclei", "labels": _LD,
        },
    },
    "calcein": {
        "cells": {
            "label": "Cells only", "label_de": "Nur Zellen",
            "prompt": "Click every cell you can see, live or dead, without classifying it.",
            "prompt_de": "Klicken Sie jede erkennbare Zelle an, lebend oder tot, "
                         "ohne sie einzuordnen.",
            "default_layer": "merged",
            "labels": [{"key": "cell", "name": "Cell", "name_de": "Zelle",
                        "colour": "#f5c518", "shape": "circle", "hotkey": "1"}],
        },
        "livedead": {
            "label": "Live / dead", "label_de": "Lebend / tot",
            "prompt": "Click every cell: green calcein means live, red EthD-1 means dead.",
            "prompt_de": "Klicken Sie jede Zelle an: grünes Calcein = lebend, "
                         "rotes EthD-1 = tot.",
            "default_layer": "merged", "labels": _LD,
        },
    },
}


def apply_config(path):
    """Load a study config and override the built-in defaults.

    This is what makes the app reusable for a different stain, a different
    tissue or a different depth range without touching any code. Everything the
    build assumes about the images lives here: where they are, how they are
    named, which channel carries which dye, how the grid is cut, and the wording
    the counters see in both languages.

    See study.example.json. Any key may be omitted; omitted keys keep their
    default. Wording supplied here is merged into the built-in tables, so you can
    override just one hint without restating all of them.
    """
    global CONFOCAL, COLS, ROWS, Z_UM, FIELD_WIDTH_UM, DEFAULT_STACKS
    cfg = json.loads(Path(path).read_text())

    if "source_root" in cfg:
        CONFOCAL = (REPO / cfg["source_root"]) if not Path(cfg["source_root"]).is_absolute()                    else Path(cfg["source_root"])
    if "grid" in cfg:
        COLS = "".join(cfg["grid"].get("cols", COLS))
        ROWS = "".join(str(r) for r in cfg["grid"].get("rows", ROWS))
    Z_UM = float(cfg.get("z_um", Z_UM))
    FIELD_WIDTH_UM = float(cfg.get("field_width_um", FIELD_WIDTH_UM))
    if "stacks" in cfg:
        DEFAULT_STACKS = cfg["stacks"]

    for name, sc in (cfg.get("schemes") or {}).items():
        base = dict(SCHEMES.get(name, {"nuclei": None, "dead": None, "live": None}))
        base.update({k: v for k, v in sc.items()
                     if k in ("desc", "nuclei", "dead", "live")})
        SCHEMES[name] = base
        if "layers" in sc:
            LAYERS_BY_SCHEME[name] = sc["layers"]
        if "modes" in sc:
            MODES_BY_SCHEME[name] = sc["modes"]
        LAYERS_BY_SCHEME.setdefault(name, LAYERS_BY_SCHEME["hoechst"])
        MODES_BY_SCHEME.setdefault(name, MODES_BY_SCHEME["hoechst"])
    return cfg


# --------------------------------------------------------------------- sources
def resolve_stack(specimen, image):
    """Map z index -> path for confocal/<specimen>/<region>/<image>_zNN.png."""
    base = CONFOCAL / specimen
    if not base.is_dir():
        raise SystemExit(f"no confocal directory for specimen {specimen}: {base}")
    pat = re.compile(re.escape(image) + r"_z(\d+)\.png$")
    found = {}
    for p in base.rglob(f"{image}_z*.png"):
        if "imaganalysis" in p.parts:
            continue
        m = pat.match(p.name)
        if m:
            found[int(m.group(1))] = p
    if not found:
        raise SystemExit(f"no slices found for {specimen}/{image}")
    regions = {p.parent.name for p in found.values()}
    if len(regions) > 1:
        raise SystemExit(f"{specimen}/{image} appears in several regions: {regions}")
    return found, regions.pop()


def resolve_legacy(specimen, image):
    base = CONFOCAL / specimen
    hits = [p for p in base.rglob(image) if "imaganalysis" not in p.parts]
    if not hits:
        raise SystemExit(f"source image not found: {specimen}/{image}")
    return hits[0]


def check_downloaded(path):
    """OneDrive placeholders read as zero-byte-allocated files and stall on open."""
    if path.stat().st_blocks == 0:
        raise SystemExit(
            f"\n{path.relative_to(REPO)} has not downloaded from OneDrive yet.\n"
            f"In Finder, right-click confocal/ and choose 'Always keep on this "
            f"device', wait for the green tick, then run this again.")


def channel_report(arr):
    out = {}
    for name, i in CH.items():
        ch = arr[..., i]
        out[name] = {
            "max": int(ch.max()),
            "mean": round(float(ch.mean()), 2),
            "p99": round(float(np.percentile(ch, 99)), 1),
            "frac_above_10": round(float((ch > 10).mean()), 4),
        }
    return out


def detect_scheme(stats):
    has = {c: stats[c]["max"] > 0 for c in "RGB"}
    if has["B"] and not has["G"]:
        return "hoechst"
    if has["G"] and not has["B"]:
        return "calcein"
    return None


def load_slice(spec, z, path, region, args):
    check_downloaded(path)
    arr = np.array(Image.open(path).convert("RGB"))
    stats = channel_report(arr)
    scheme = SCHEMES[args.scheme]
    roles = {v: k for k, v in scheme.items() if k in ("nuclei", "dead", "live") and v}

    found = detect_scheme(stats)
    if found and found != args.scheme:
        raise SystemExit(
            f"  {spec['specimen']}/{spec['image']}_z{z:02d}: channel occupancy says this "
            f"is the {found!r} scheme, but --scheme {args.scheme!r} was requested.")
    for role, name in roles.items():
        if stats[role]["max"] == 0:
            raise SystemExit(f"  {path.name}: {name} channel {role} is empty")

    return {"spec": spec, "z": z, "path": path, "region": region,
            "arr": arr, "stats": stats, "roles": roles, "scheme": scheme,
            "stack_key": f"{spec['specimen']}/{region}/{spec['image']}"}


# ------------------------------------------------------------------- rendering
def compute_cuts(loaded, args):
    """Black and white points, pooled over every field in the build.

    One set of levels for the whole build means identical nuclei look identical
    at every depth. Stretching each slice separately would brighten the deep,
    dim ones back up and erase the depth effect being measured.
    """
    names = sorted({n for f in loaded for n in f["roles"].values()})
    cuts = {}
    for name in names:
        vals = [f["arr"][..., CH[r]].ravel()
                for f in loaded for r, n in f["roles"].items() if n == name]
        pool = np.concatenate(vals) if len(vals) > 1 else vals[0]
        lo = float(np.percentile(pool, args.lo_pct))
        hi = float(np.percentile(pool, args.hi_pct))
        cuts[name] = (lo, max(hi, lo + 1.0))
    return cuts


def stretch_to(arr, chan_idx, lo, hi):
    v = (arr[..., chan_idx].astype(np.float32) - lo) / max(hi - lo, 1.0)
    return (np.clip(v, 0.0, 1.0) * 255.0).astype(np.uint8)


def square_bounds(w, h, ci, ri):
    cw, ch = w / len(COLS), h / len(ROWS)
    return (int(round(ci * cw)), int(round(ri * ch)),
            int(round((ci + 1) * cw)), int(round((ri + 1) * ch)))


def signal_per_square(fld, cuts):
    """Mean stretched intensity of the counting channel in each grid square."""
    key = "nuclei" if fld["scheme"]["nuclei"] else "live"
    role = fld["scheme"][key]
    lo, hi = cuts[key]
    img = stretch_to(fld["arr"], CH[role], lo, hi)
    h, w = img.shape
    out = {}
    for ri in range(len(ROWS)):
        for ci in range(len(COLS)):
            x0, y0, x1, y1 = square_bounds(w, h, ci, ri)
            out[f"{COLS[ci]}{ROWS[ri]}"] = float(img[y0:y1, x0:x1].mean())
    return out


def choose_squares(stack_signal, n, seed):
    """Pick n squares per stack, stratified by how much signal they hold.

    Sampling across strata keeps dense, sparse and empty squares all in the set.
    Empty squares are kept on purpose: they are the only place a false positive
    can be seen, and dropping them would flatter everyone's agreement.

    Chosen once per stack and reused at every depth, so the same x,y location is
    counted at each z and depth can be compared within location.
    """
    squares = sorted(stack_signal, key=lambda s: (-stack_signal[s], s))
    if n <= 0 or n >= len(squares):
        return squares
    rng = np.random.default_rng(seed)
    strata = np.array_split(np.array(squares), 4)
    per = max(1, n // 4)
    picked = []
    for band in strata:
        take = min(per, len(band))
        picked.extend(rng.choice(band, size=take, replace=False).tolist())
    leftover = [s for s in squares if s not in set(picked)]
    rng.shuffle(leftover)
    picked.extend(leftover[:max(0, n - len(picked))])
    return sorted(picked[:n])


def build_field(fld, field_no, args, tiles_dir, cuts, squares):
    spec, arr, roles, scheme = fld["spec"], fld["arr"], fld["roles"], fld["scheme"]
    h, w = arr.shape[:2]

    chans = {name: stretch_to(arr, CH[role], *cuts[name]) for role, name in roles.items()}
    zero = np.zeros(arr.shape[:2], np.uint8)
    dead = chans["dead"]

    layers = {"dead": Image.fromarray(dead).convert("RGB")}
    if scheme["nuclei"]:
        nuc = chans["nuclei"]
        layers["nuclei"] = Image.fromarray(nuc).convert("RGB")
        layers["merged"] = Image.fromarray(np.dstack([dead, zero, nuc]))
    else:
        live = chans["live"]
        layers["live"] = Image.fromarray(live).convert("RGB")
        layers["merged"] = Image.fromarray(np.dstack([dead, live, zero]))

    margin = int(round(min(w / len(COLS), h / len(ROWS)) * args.context))
    up = args.upscale
    resample = RESAMPLE[args.resample]

    segments = []
    for ri, rlab in enumerate(ROWS):
        for ci, clab in enumerate(COLS):
            sq = f"{clab}{rlab}"
            if sq not in squares:
                continue
            if ONLY_SQUARES and sq not in ONLY_SQUARES:
                continue
            x0, y0, x1, y1 = square_bounds(w, h, ci, ri)
            tx0, ty0 = max(0, x0 - margin), max(0, y0 - margin)
            tx1, ty1 = min(w, x1 + margin), min(h, y1 + margin)
            tw, th = (tx1 - tx0) * up, (ty1 - ty0) * up

            seg_id = f"f{field_no}_{sq}"
            files = {}
            for name, im in layers.items():
                tile = im.crop((tx0, ty0, tx1, ty1))
                if up != 1:
                    tile = tile.resize((tw, th), resample)
                out = tiles_dir / f"{seg_id}_{name}.png"
                tile.save(out, optimize=True)
                files[name] = f"tiles/{out.name}"

            segments.append({
                "id": seg_id, "field": field_no, "square": sq,
                "col": clab, "row": rlab,
                "z": fld["z"], "depth_um": round(fld["z"] * Z_UM, 1),
                # same x,y in the same stack at any depth -> same location
                "location": f"{fld['stack_key']}/{sq}",
                "tile_w": tw, "tile_h": th,
                "count_box": [(x0 - tx0) * up, (y0 - ty0) * up,
                              (x1 - tx0) * up, (y1 - ty0) * up],
                "tile_origin": [tx0, ty0], "upscale": up,
                "layers": files,
            })

    field_meta = {
        "field": field_no,
        "specimen": spec["specimen"], "region": fld["region"],
        "stack": spec["image"], "z": fld["z"],
        "depth_um": round(fld["z"] * Z_UM, 1),
        "source": str(fld["path"].relative_to(REPO)),
        "width": w, "height": h,
        "grid": {"cols": list(COLS), "rows": list(ROWS)},
        "scheme": args.scheme, "scheme_desc": scheme["desc"],
        "um_per_px": round(args.field_width_um / w, 4),
        "square_um": round(args.field_width_um / len(COLS), 1),
        "channels": {**{k: v for k, v in scheme.items()
                        if k in ("nuclei", "dead", "live")}, "stats": fld["stats"]},
        "n_squares": len(segments),
    }
    return field_meta, segments


# ---------------------------------------------------------------- from-grid
PANEL_ROLE = ["merged", "nuclei", "dead"]


def _runs(mask):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1)); start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


def find_panels(a):
    """Locate the three panel axes in a COUNT_field_*_grid.png figure."""
    H, W, _ = a.shape
    green = (a[..., 1] > 110) & (a[..., 0] < 90) & (a[..., 2] < 90)
    # A grid line runs the full extent of its panel; the green A1..H8 cell labels
    # are short. Requiring half the figure's extent keeps lines and drops labels.
    nx, ny = len(COLS) - 1, len(ROWS) - 1
    xs = [c for c, _ in _runs(green.sum(0) > H * 0.50)]
    ys = [r for r, _ in _runs(green.sum(1) > W * 0.50)]
    if len(xs) != nx * 3:
        raise SystemExit(f"expected {nx*3} vertical grid lines (3 panels x {nx}), "
                         f"found {len(xs)}")
    if len(ys) != ny:
        raise SystemExit(f"expected {ny} horizontal grid lines, found {len(ys)}: {ys}")
    pitch = (xs[nx - 1] - xs[0]) / (nx - 1)
    top, bot = ys[0] - pitch, ys[ny - 1] + pitch
    panels = [(xs[k * nx] - pitch, top, xs[k * nx + nx - 1] + pitch, bot) for k in range(3)]
    return panels, pitch, green


def despeckle_green(img, green, line_px=3):
    """Erase the baked-in grid lines and cell labels, filling from neighbours.

    The median window has to be wide enough that the line is a MINORITY inside
    it. These lines are 3 px of core plus an anti-aliased pixel each side, so a
    5x5 median is still mostly line and helpfully replaces green with green. Use
    at least 3x the line width, and dilate the mask to catch the soft flanks the
    colour threshold misses.
    """
    from PIL import ImageFilter
    win = max(5, (line_px * 3) | 1)          # odd, >= 3x the line width
    med = img.filter(ImageFilter.MedianFilter(win))
    out = np.array(img)
    m = np.array(Image.fromarray(green.astype(np.uint8) * 255)
                 .filter(ImageFilter.MaxFilter(5))) > 0
    out[m] = np.array(med)[m]
    return Image.fromarray(out)


def build_field_from_grid(spec, args, tiles_dir):
    """Cut tiles straight out of COUNT_field_N_grid.png -- the exact stimulus
    Maryam and Louise counted, with no channel or stretch decisions to make."""
    path = GRID_DIR / f"COUNT_field_{spec['field']}_grid.png"
    if not path.exists():
        raise SystemExit(f"grid figure not found: {path}")
    check_downloaded(path)
    fig = Image.open(path).convert("RGB")
    panels, pitch, green = find_panels(np.array(fig).astype(int))
    clean = despeckle_green(fig, green) if args.clean_grid else fig

    layers = {role: clean.crop(tuple(int(round(v)) for v in box))
              for role, box in zip(PANEL_ROLE, panels)}
    w, h = layers["merged"].size
    margin = int(round(min(w / len(COLS), h / len(ROWS)) * args.context))

    segments = []
    for ri, rlab in enumerate(ROWS):
        for ci, clab in enumerate(COLS):
            x0, y0, x1, y1 = square_bounds(w, h, ci, ri)
            tx0, ty0 = max(0, x0 - margin), max(0, y0 - margin)
            tx1, ty1 = min(w, x1 + margin), min(h, y1 + margin)
            sq = f"{clab}{rlab}"
            if ONLY_SQUARES and sq not in ONLY_SQUARES:
                continue
            seg_id = f"f{spec['field']}_{sq}"
            files = {}
            for role, im in layers.items():
                out = tiles_dir / f"{seg_id}_{role}.png"
                im.crop((tx0, ty0, tx1, ty1)).save(out, optimize=True)
                files[role] = f"tiles/{out.name}"
            segments.append({
                "id": seg_id, "field": spec["field"], "square": sq,
                "col": clab, "row": rlab, "z": None, "depth_um": None,
                "location": f"{spec['specimen']}/grid/{spec['image']}/{sq}",
                "tile_w": tx1 - tx0, "tile_h": ty1 - ty0,
                "count_box": [x0 - tx0, y0 - ty0, x1 - tx0, y1 - ty0],
                "tile_origin": [tx0, ty0], "upscale": 1, "layers": files,
            })

    field_meta = {
        "field": spec["field"], "specimen": spec["specimen"], "region": "(from figure)",
        "stack": spec["image"], "z": None, "depth_um": None,
        "source": str(path.relative_to(REPO)), "width": w, "height": h,
        "grid": {"cols": list(COLS), "rows": list(ROWS)},
        "scheme": "hoechst", "scheme_desc": "as rendered in the original figure",
        "um_per_px": round(args.field_width_um / w, 4),
        "square_um": round(args.field_width_um / len(COLS), 1),
        "built_from": "COUNT_field_*_grid.png panels A/B/C",
        "grid_lines_removed": bool(args.clean_grid),
        "n_squares": len(segments),
    }
    return field_meta, segments


# ------------------------------------------------------------------ assignment
def load_training(path, n, segments, match_um, fields_meta, gate=(0.90, 0.90)):
    """Turn a reference counter's exported session into a training round.

    Britten-Jones et al. (2022) found that a consensus training step was what
    actually removed systematic inter-observer bias in manual cell counting on
    confocal images. This builds that step from an expert's own pass through the
    app: their marks become the reference answer shown as feedback.

    Deliberately NOT derived from the automated detector -- that is the thing
    being validated, and training counters against it would make the comparison
    circular.
    """
    sess = json.loads(Path(path).read_text())
    by_id = {s["id"]: s for s in segments}
    um_per_px = {f["field"]: f.get("um_per_px", 1.0) for f in fields_meta}

    ref = {}
    for key, st in sess.get("seg", {}).items():
        seg_id = key.split("#")[0]
        if seg_id not in by_id:
            continue
        if not st.get("done"):
            continue
        # a square the expert marked empty is a valid reference: zero nuclei
        ref.setdefault(seg_id, [{"x": m["x"], "y": m["y"], "label": m["label"]}
                                for m in st.get("marks", [])])

    if not ref:
        raise SystemExit(f"{path} has no completed squares that match this build")

    # Prefer squares with something to learn from: a mix of busy and sparse,
    # busiest first, since an empty square teaches nothing about where to click.
    order = sorted(ref, key=lambda k: (-len(ref[k]), k))
    chosen = order[:n] if n and n < len(order) else order
    radius = {sid: match_um / um_per_px.get(by_id[sid]["field"], 1.0) for sid in chosen}

    return {
        "segments": chosen,
        "reference": {sid: ref[sid] for sid in chosen},
        "match_radius_px": {sid: round(radius[sid], 2) for sid in chosen},
        "source": Path(path).name,
        "rater": sess.get("rater", "reference"),
        "mode": sess.get("mode"),
        "own_pairwise_f1": sess.get("own_pairwise_f1"),
        "passes_per_square": sess.get("passes_per_square"),
        "gate": {"min_count_accuracy": gate[0], "min_location_f1": gate[1]},
    }


def assign_blocks(segments, n_blocks, replicates, n_anchors, seed,
                  repeat_fraction=0.0, repeat_gap=12):
    """Spread segments over blocks, with two constraints that protect the design.

    * Anchors go to every block, so all counters share common ground.
    * No block ever contains the same `location` twice. A counter therefore never
      meets the same x,y square at two depths -- at the second one they would be
      recalling their earlier answer instead of counting.

    Every non-anchor segment is placed in `replicates` different blocks so
    pairwise agreement is estimable everywhere.
    """
    rng = np.random.default_rng(seed)
    by_field = {}
    for s in segments:
        by_field.setdefault(s["field"], []).append(s["id"])
    loc = {s["id"]: s["location"] for s in segments}

    anchors = []
    if n_anchors:
        per_field = max(1, n_anchors // max(1, len(by_field)))
        for f in sorted(by_field):
            ids = sorted(by_field[f])
            anchors.extend(rng.choice(ids, size=min(per_field, len(ids)),
                                      replace=False).tolist())
        # anchors must not collide with each other on location either
        seen, keep = set(), []
        for a in sorted(set(anchors)):
            if loc[a] in seen:
                continue
            seen.add(loc[a]); keep.append(a)
        anchors = keep[:n_anchors]

    names = [f"B{i + 1:02d}" for i in range(n_blocks)]
    blocks = {n: list(anchors) for n in names}
    taken = {n: {loc[a] for a in anchors} for n in names}

    order = sorted(s["id"] for s in segments if s["id"] not in set(anchors))
    rng.shuffle(order)

    skipped = 0
    k = 0
    for _ in range(replicates):
        for sid in order:
            placed = False
            for attempt in range(n_blocks):
                b = names[(k + attempt) % n_blocks]
                if loc[sid] not in taken[b]:
                    blocks[b].append(sid); taken[b].add(loc[sid])
                    placed = True; break
            k += 1
            if not placed:
                skipped += 1

    # Shuffle each block. Otherwise every counter meets the anchors first, while
    # least practised -- an order effect landing on exactly the squares used to
    # put all the counters on one scale. Depths end up interleaved too, so nobody
    # counts a run of deep squares in a row.
    for i, n in enumerate(names):
        sub = np.random.default_rng(seed + 1000 + i)
        arr = np.array(blocks[n], dtype=object)
        sub.shuffle(arr)
        blocks[n] = arr.tolist()

    if repeat_fraction > 0:
        for i, n in enumerate(names):
            blocks[n] = insert_repeats(blocks[n], repeat_fraction,
                                       np.random.default_rng(seed + 2000 + i),
                                       repeat_gap)
    return anchors, blocks, skipped


def insert_repeats(order, fraction, rng, min_gap=12):
    """Show some squares to the same counter twice, far apart in their sequence.

    This measures INTRA-rater reliability (test-retest): the same person, the
    same image, twice. It is a different quantity from inter-rater reliability,
    which comes from --replicates handing one square to several people.

    Intra-rater agreement is the ceiling for inter-rater agreement -- two people
    cannot agree with each other more closely than each agrees with themselves --
    so without it a poor inter-rater result cannot be attributed to the counters
    disagreeing rather than to the task being irreducibly ambiguous.

    Repeats are drawn from the first half and placed in the second half, at least
    `min_gap` squares later, so the counter is recalling as little as possible.
    GRRAS (Kottner 2011) asks for the interval between repeated measurements to
    be reported; that is `min_gap` and it goes in the manifest.
    """
    n = len(order)
    k = max(1, int(round(n * fraction)))
    half = max(1, n // 2)
    k = min(k, half)

    picks = rng.choice(np.arange(half), size=k, replace=False)
    out = list(order)
    for src in sorted(picks, reverse=True):
        lo = max(int(src) + min_gap, len(out) // 2)
        if lo >= len(out):
            lo = len(out) - 1
        pos = int(rng.integers(lo, len(out) + 1)) if lo < len(out) else len(out)
        out.insert(pos, order[int(src)])
    return out


# ------------------------------------------------------------------------ main
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="",
                   help="study config JSON: source folder, stacks, grid, dye channels "
                        "and the wording counters see. This is how you point the app "
                        "at a different stain, tissue or depth range without editing "
                        "code. See study.example.json")
    p.add_argument("--study", default="SCLERA-LIVE manual count v2")
    p.add_argument("--stacks", default="",
                   help="comma-separated specimen/Image N, e.g. '003/Image 5,006/Image 11'. "
                        "Defaults to the five manual-count stacks")
    p.add_argument("--z-levels", default="5,9,13,17",
                   help=f"z slices to sample from every stack ({Z_UM} um apart). "
                        f"Depth becomes a factor you can test rather than a constant")
    p.add_argument("--only-squares", default="",
                   help="build only these grid squares, e.g. 'F5,E1,F4,F2,G6'. Used to "
                        "make a small reference set from the squares two counters "
                        "already agreed on (see analysis/legacy_agreement.py)")
    p.add_argument("--reference-passes", type=int, default=0,
                   help="build a REF block containing the squares --reference-passes "
                        "times over, shuffled between passes, so one person can count "
                        "them repeatedly and their agreed answer becomes the reference")
    p.add_argument("--squares-per-field", type=int, default=0,
                   help="sample this many of the 64 squares per stack, stratified by "
                        "signal (0 = all 64). The same squares are used at every depth")
    p.add_argument("--blocks", type=int, default=20, help="number of rater blocks")
    p.add_argument("--replicates", type=int, default=3,
                   help="how many different blocks each segment appears in")
    p.add_argument("--anchors", type=int, default=5,
                   help="segments given to every rater as a common calibration set")
    p.add_argument("--repeat-fraction", type=float, default=0.15,
                   help="fraction of each counter's set shown to them a second time, "
                        "far later in their sequence, to measure intra-rater "
                        "(test-retest) reliability. 0 disables")
    p.add_argument("--repeat-gap", type=int, default=12,
                   help="minimum number of squares between a repeat and its original")
    p.add_argument("--context", type=float, default=0.12,
                   help="context margin around each square, as a fraction of square size")
    p.add_argument("--upscale", type=int, default=1,
                   help="integer display upscale. Leave at 1: the app zooms, and browser "
                        "interpolation matches PIL's while keeping the tiles small")
    p.add_argument("--resample", default="bicubic", choices=sorted(RESAMPLE))
    p.add_argument("--stretch", default="global", choices=["global", "per-field"],
                   help="global (default) uses one set of cut levels for every field, so "
                        "a deep dim slice renders dim instead of having its noise "
                        "stretched up into plausible nuclei")
    p.add_argument("--lo-pct", type=float, default=1.0)
    p.add_argument("--hi-pct", type=float, default=99.7)
    p.add_argument("--scheme", default="hoechst", choices=sorted(SCHEMES),
                   help="hoechst = Hoechst 33342 + EthD-1 (all nuclei plus dead, the "
                        "scheme this task needs); calcein = calcein + EthD-1 (no total)")
    p.add_argument("--consent", default="",
                   help="show the plain-language information and consent page before "
                        "the tool opens, e.g. --consent 1.0 for consent version 1.0. "
                        "Required for the participant round; the expert panel consent "
                        "by email instead")
    p.add_argument("--identity", default="name", choices=["name", "code"],
                   help="how counters identify themselves. 'name' for the expert "
                        "panel; 'code' for participants — the app generates an "
                        "anonymous code they keep, so no name is ever collected and "
                        "no name-to-code key exists for anyone to hold")
    p.add_argument("--endpoint", default="",
                   help="Google Apps Script /exec URL for auto-submit (optional)")
    p.add_argument("--field-width-um", type=float, default=FIELD_WIDTH_UM)
    p.add_argument("--seconds-per-square", type=float, default=45.0,
                   help="used only to estimate how long a counter's set will take")
    p.add_argument("--seed", type=int, default=20260823)
    p.add_argument("--prefill-from", default="",
                   help="a reference_proposal.json from tools/propose_reference.py. "
                        "Its marks are placed on each square for you to CORRECT. "
                        "Only ever use this for authoring a reference, never for a "
                        "participant's set -- seeing a detector's answer first would "
                        "anchor them to it")
    p.add_argument("--training-from", default="",
                   help="an exported *_session.json from a reference counter. Its "
                        "squares become a training round every counter does first, "
                        "with the reference answer shown as feedback after each one")
    p.add_argument("--gate-count", type=float, default=0.90,
                   help="participants must reach this accuracy on the NUMBER of "
                        "nuclei across the practice squares before their real counts "
                        "are kept (0 disables the gate)")
    p.add_argument("--gate-location", type=float, default=0.90,
                   help="and this detection F1 on WHICH nuclei, matched by position")
    p.add_argument("--training-n", type=int, default=6,
                   help="how many training squares to use from that session")
    p.add_argument("--match-um", type=float, default=8.0,
                   help="two marks are the same nucleus within this distance; used "
                        "for training feedback and for analysis")
    p.add_argument("--from-grid", action="store_true",
                   help="cut tiles from COUNT_field_N_grid.png instead: identical "
                        "stimulus to the Maryam / Louise round, single depth only")
    p.add_argument("--no-clean-grid", dest="clean_grid", action="store_false",
                   help="with --from-grid, keep the green grid lines and cell labels")
    p.add_argument("--fields", default="", help="with --from-grid, subset e.g. 1,2")
    p.add_argument("--out", default="docs", help="output directory (default docs/)")
    p.add_argument("--clean", action="store_true", help="wipe the tiles directory first")
    args = p.parse_args()

    global ONLY_SQUARES
    ONLY_SQUARES = {x.strip().upper() for x in args.only_squares.split(",") if x.strip()}

    cfg = apply_config(args.config) if args.config else {}
    if cfg.get("study") and args.study == p.get_default("study"):
        args.study = cfg["study"]
    if cfg.get("z_levels") and args.z_levels == p.get_default("z_levels"):
        args.z_levels = ",".join(str(z) for z in cfg["z_levels"])
    if cfg.get("scheme") and args.scheme == p.get_default("scheme"):
        args.scheme = cfg["scheme"]
    if args.scheme not in SCHEMES:
        raise SystemExit(f"unknown scheme {args.scheme!r}; "
                         f"known: {', '.join(sorted(SCHEMES))}")

    docs = APP_DIR / args.out
    tiles_dir = docs / "tiles"
    if args.clean and tiles_dir.exists():
        shutil.rmtree(tiles_dir)
    tiles_dir.mkdir(parents=True, exist_ok=True)

    fields_meta, all_segments = [], []

    if args.from_grid:
        wanted = {int(x) for x in args.fields.split(",") if x.strip()}
        for spec in LEGACY_FIELDS:
            if wanted and spec["field"] not in wanted:
                continue
            print(f"field {spec['field']}: {spec['specimen']}/{spec['image']}", flush=True)
            fm, segs = build_field_from_grid(spec, args, tiles_dir)
            print(f"    {fm['width']}x{fm['height']} px, {len(segs)} segments")
            fields_meta.append(fm)
            all_segments.extend(segs)
    else:
        stacks = ([{"specimen": s.split("/", 1)[0].strip(),
                    "image": s.split("/", 1)[1].strip()}
                   for s in args.stacks.split(",") if s.strip()]
                  or DEFAULT_STACKS)
        zs = sorted({int(z) for z in args.z_levels.split(",") if z.strip()})

        # pass 1 -- read every slice and check its channels
        loaded = []
        for spec in stacks:
            zmap, region = resolve_stack(spec["specimen"], spec["image"])
            missing = [z for z in zs if z not in zmap]
            if missing:
                raise SystemExit(f"{spec['specimen']}/{spec['image']}: no slices "
                                 f"{missing} (stack has z{min(zmap):02d}..z{max(zmap):02d})")
            print(f"{spec['specimen']}/{region}/{spec['image']}: "
                  f"z{'  z'.join(f'{z:02d}' for z in zs)}", flush=True)
            for z in zs:
                loaded.append(load_slice(spec, z, zmap[z], region, args))

        # pass 2 -- one set of cut levels for the whole build
        cuts = compute_cuts(loaded, args)
        print(f"\ndisplay stretch ({args.stretch}), percentiles "
              f"{args.lo_pct}-{args.hi_pct}:")
        for name, (lo, hi) in cuts.items():
            print(f"    {name:7s} black={lo:6.1f}  white={hi:6.1f}")

        # pass 3 -- choose squares once per stack, so depth is compared in place
        per_stack = {}
        for fld in loaded:
            per_stack.setdefault(fld["stack_key"], []).append(fld)
        chosen = {}
        for key, flds in per_stack.items():
            sig = {}
            for fld in flds:
                for sq, v in signal_per_square(fld, cuts).items():
                    sig[sq] = max(sig.get(sq, 0.0), v)
            chosen[key] = set(choose_squares(sig, args.squares_per_field, args.seed))

        # pass 4 -- render
        print("\nfields:")
        for n, fld in enumerate(loaded, 1):
            fcuts = compute_cuts([fld], args) if args.stretch == "per-field" else cuts
            fm, segs = build_field(fld, n, args, tiles_dir, fcuts,
                                   chosen[fld["stack_key"]])
            key = "nuclei" if fld["scheme"]["nuclei"] else "live"
            p99 = fld["stats"][fld["scheme"][key]]["p99"]
            flag = "  <- weak, consider dropping" if p99 < cuts[key][1] * 0.25 else ""
            print(f"    {n:3d}  {fm['specimen']}/{fm['region']}/{fm['stack']} "
                  f"z{fm['z']:02d} ({fm['depth_um']:5.1f} um)  "
                  f"{len(segs):3d} squares  {key} p99={p99:5.1f}{flag}")
            fields_meta.append(fm)
            all_segments.extend(segs)

    if not all_segments:
        raise SystemExit("no fields built")

    training = (load_training(args.training_from, args.training_n, all_segments,
                              args.match_um, fields_meta,
                              (args.gate_count, args.gate_location))
                if args.training_from else None)

    # A training square must never appear in anyone's real set: they have just
    # been shown its reference answer, so counting it again measures memory.
    train_ids = set(training["segments"]) if training else set()
    assignable = [s for s in all_segments if s["id"] not in train_ids]
    if training and not assignable:
        raise SystemExit("every segment is a training square -- lower --training-n")

    prefill = None
    if args.prefill_from:
        pf = json.loads(Path(args.prefill_from).read_text())
        prefill = {}
        for key, st in (pf.get("seg") or {}).items():
            prefill.setdefault(key.split("#")[0],
                               [{"x": m["x"], "y": m["y"], "label": m.get("label", "cell")}
                                for m in st.get("marks", [])])
        print(f"prefill: {sum(len(v) for v in prefill.values())} proposed marks on "
              f"{len(prefill)} squares (a DRAFT to correct, not an answer)")

    if args.reference_passes > 1 and prefill:
        raise SystemExit(
            "\n--prefill-from with --reference-passes > 1 is refused, on purpose.\n\n"
            "Every pass would start from the SAME draft, so your passes would agree\n"
            "with each other because they began identically, not because you saw the\n"
            "same thing twice. That inflates your between-pass agreement -- the one\n"
            "number used to decide whether a 90% gate is fair -- and would make an\n"
            "unfair gate look justified.\n\n"
            "Pick one:\n"
            "  --reference-passes 3                    independent passes, slower, honest\n"
            "  --prefill-from ... --reference-passes 1  one assisted pass, detector-anchored\n")

    if args.reference_passes:
        # One person counts the same few squares several times over. Their
        # repeats are then combined into a consensus reference, and the spread
        # between their own passes says how firm that reference actually is.
        ids = [s["id"] for s in all_segments]
        rng = np.random.default_rng(args.seed)
        order = []
        for _ in range(args.reference_passes):
            a = np.array(ids, dtype=object); rng.shuffle(a)
            order.extend(a.tolist())
        manifest_blocks = {"REF": order}
        out = docs / "manifest.json"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "manifest.json").write_text(json.dumps({
            "schema": "sclera-count-manifest-v1",
            "study": args.study + " — reference pass",
            "built_by": "build_segments.py --reference-passes",
            "endpoint": args.endpoint, "modes": MODES_BY_SCHEME[args.scheme],
            "layers": LAYERS_BY_SCHEME[args.scheme],
            "fields": fields_meta, "segments": all_segments,
            "anchors": [], "blocks": manifest_blocks, "training": None,
            "prefill": prefill, "identity": args.identity,
            "consent": ({"version": args.consent} if args.consent else None),
            "match_um": args.match_um,
            "assignment": {"reference_passes": args.reference_passes,
                           "seed": args.seed},
            "tiling": {"built_from": "grid_figure" if args.from_grid else "confocal_source",
                       "context_margin_fraction": args.context,
                       "upscale": args.upscale, "resample": args.resample, "z_um": Z_UM},
            "display_stretch": {"mode": args.stretch, "lo_pct": args.lo_pct,
                                "hi_pct": args.hi_pct},
        }, indent=1))
        n_tiles = len(list(tiles_dir.glob("*.png")))
        print(f"\nREFERENCE BUILD: {len(all_segments)} squares x "
              f"{args.reference_passes} passes = {len(order)} to count")
        print(f"  squares: {', '.join(sorted({s['square'] for s in all_segments}))}")
        print(f"  wrote {out} ({n_tiles} tiles)")
        print("\n  Count all of them, press Download my counts, then:")
        print("    /usr/bin/python3 analysis/make_reference.py <the _session.json>")
        return

    anchors, blocks, skipped = assign_blocks(assignable, args.blocks, args.replicates,
                                             args.anchors, args.seed,
                                             args.repeat_fraction, args.repeat_gap)

    manifest = {
        "schema": "sclera-count-manifest-v1",
        "study": args.study,
        "built_by": "build_segments.py",
        "endpoint": args.endpoint,
        "modes": MODES_BY_SCHEME[args.scheme],
        "layers": LAYERS_BY_SCHEME[args.scheme],
        "fields": fields_meta,
        "segments": all_segments,
        "anchors": anchors,
        "blocks": blocks,
        "training": training,
        "prefill": prefill,
        "identity": args.identity,
        "consent": ({"version": args.consent} if args.consent else None),
        "match_um": args.match_um,
        "assignment": {
            "n_blocks": args.blocks, "replicates": args.replicates,
            "n_anchors": len(anchors), "seed": args.seed,
            "one_depth_per_location": True,
            "placements_dropped": skipped,
            "repeat_fraction": args.repeat_fraction,
            "repeat_min_gap": args.repeat_gap,
        },
        "tiling": {
            "built_from": "grid_figure" if args.from_grid else "confocal_source",
            "context_margin_fraction": args.context,
            "upscale": args.upscale, "resample": args.resample,
            "z_um": Z_UM,
        },
        "display_stretch": {
            "mode": args.stretch, "lo_pct": args.lo_pct, "hi_pct": args.hi_pct,
        },
    }
    if not args.from_grid:
        manifest["display_stretch"]["cuts"] = {k: list(v) for k, v in cuts.items()}

    out = docs / "manifest.json"
    out.write_text(json.dumps(manifest, indent=1))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()[:12]

    n_tiles = len(list(tiles_dir.glob("*.png")))
    size_mb = sum(f.stat().st_size for f in tiles_dir.glob("*.png")) / 1e6
    per_block = len(next(iter(blocks.values())))
    mins = per_block * args.seconds_per_square / 60.0

    if args.config:
        print(f"\nconfig: {args.config}")
    print(f"\nwrote {out}  ({len(all_segments)} segments, sha256:{digest})")
    print(f"tiles: {n_tiles} files, {size_mb:.1f} MB")
    first = next(iter(blocks.values()))
    n_rep = len(first) - len(set(first))
    print(f"blocks: {args.blocks} counters x {per_block} squares "
          f"(~{mins:.0f} min each at {args.seconds_per_square:.0f}s a square)")
    if n_rep:
        print(f"        of those, {n_rep} are repeats of squares they already counted "
              f"(>= {args.repeat_gap} apart) for intra-rater reliability")
    print(f"        {args.replicates}x coverage, {len(anchors)} anchors shared by all,"
          f" no counter sees one location at two depths")
    if skipped:
        print(f"        {skipped} placements dropped: too few blocks to hold "
              f"{args.replicates} copies without repeating a location. "
              f"Raise --blocks or lower --replicates.")
    if training:
        n_ref = sum(len(v) for v in training["reference"].values())
        print(f"training: {len(training['segments'])} squares from "
              f"{training['rater']} ({n_ref} reference marks), shown to everyone "
              f"first with feedback")
        print(f"        held out of every counting set, so nobody counts a square "
              f"whose answer they were shown")
        if args.gate_count or args.gate_location:
            print(f"        gate: participants must reach "
                  f"{100*args.gate_count:.0f}% on number and "
                  f"{100*args.gate_location:.0f}% on location to start the real squares")
        own = training.get("own_pairwise_f1")
        if own is not None and own < args.gate_location:
            print(f"        WARNING: the reference author's own passes agree at only "
                  f"{own:.2f}, below the {args.gate_location:.2f} gate. Participants "
                  f"would have to beat the reference's own repeatability. Lower "
                  f"--gate-location or add more reference passes.")
    else:
        print("\nno --training-from: counters go straight to live data. "
              "Britten-Jones et al. (2022) found a consensus training round is "
              "what removes systematic inter-observer bias -- see REFERENCES.md.")
    if not args.endpoint:
        print("\nno --endpoint set: the app runs in export-only mode.")


if __name__ == "__main__":
    sys.exit(main())
