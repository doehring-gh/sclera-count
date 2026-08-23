#!/usr/bin/env python3
"""
fetch_sources.py -- work out which image files a build needs, pull them down from
OneDrive, and say when you can actually build.

    /usr/bin/python3 tools/fetch_sources.py                  # what is missing?
    /usr/bin/python3 tools/fetch_sources.py --fetch          # pull them down
    /usr/bin/python3 tools/fetch_sources.py --fetch --watch  # ...and wait

Why this exists
---------------
OneDrive on macOS keeps files as placeholders until something reads them, and it
gives no progress for a file nobody has opened. So "is it downloading?" has no
answer until you force the issue. This asks for exactly the files your build
needs, in parallel, and shows what is actually arriving.

`stat -f %b` is the ground truth: a placeholder reports 0 allocated blocks no
matter what size it claims. That is what this counts.

It only ever READS. Nothing here modifies or deletes anything in OneDrive.
"""

import argparse
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_segments as B   # noqa: E402  (reuses the same stack/config resolution)


def is_local(p: Path) -> bool:
    """A OneDrive placeholder allocates no blocks, whatever size it reports."""
    try:
        return p.stat().st_blocks > 0
    except OSError:
        return False


def wanted_files(args):
    """Exactly the files the matching build_segments.py run would open."""
    out = []
    if args.from_grid:
        for spec in B.LEGACY_FIELDS:
            if args.fields and spec["field"] not in args.fields:
                continue
            out.append(B.GRID_DIR / f"COUNT_field_{spec['field']}_grid.png")
        return out

    stacks = ([{"specimen": s.split("/", 1)[0].strip(),
                "image": s.split("/", 1)[1].strip()}
               for s in args.stacks.split(",") if s.strip()]
              or B.DEFAULT_STACKS)
    zs = sorted({int(z) for z in args.z_levels.split(",") if z.strip()})
    for spec in stacks:
        try:
            zmap, _ = B.resolve_stack(spec["specimen"], spec["image"])
        except SystemExit as e:
            print(f"  ! {spec['specimen']}/{spec['image']}: {e}")
            continue
        for z in zs:
            if z in zmap:
                out.append(zmap[z])
            else:
                print(f"  ! {spec['specimen']}/{spec['image']}: no z{z:02d}")
    return out


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024


def report(files):
    have = [f for f in files if is_local(f)]
    miss = [f for f in files if not is_local(f)]
    print(f"\n{len(have)} of {len(files)} files are on this machine")
    for f in files:
        mark = "ok  " if is_local(f) else "WAIT"
        try:
            size = human(f.stat().st_size)
        except OSError:
            size = "?"
        try:
            rel = f.relative_to(B.REPO)
        except ValueError:
            rel = f
        print(f"  {mark}  {size:>8}  {rel}")
    return have, miss


def fetch(files, workers, per_file_timeout, watch, poll):
    """Ask for every missing file at once and show what actually arrives.

    One reader thread per file: a single stalled file then cannot hold up the
    rest, which is what happens if you cat them one after another.
    """
    missing = [f for f in files if not is_local(f)]
    if not missing:
        print("\nnothing to fetch.")
        return True

    print(f"\nrequesting {len(missing)} file(s), {workers} at a time…")
    print("(this asks OneDrive for them; leave it running)\n")

    todo = list(missing)
    lock = threading.Lock()
    done_flag = threading.Event()

    def worker():
        while not done_flag.is_set():
            with lock:
                if not todo:
                    return
                f = todo.pop()
            try:
                with open(f, "rb") as fh:
                    while fh.read(1 << 20):
                        if done_flag.is_set():
                            return
            except OSError:
                pass

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(workers)]
    for t in threads:
        t.start()

    start = time.time()
    last_n, stalled_for = -1, 0.0
    try:
        while True:
            n = sum(1 for f in missing if is_local(f))
            el = time.time() - start
            bar = "#" * int(24 * n / len(missing)) + "." * (24 - int(24 * n / len(missing)))
            sys.stdout.write(f"\r  [{bar}] {n}/{len(missing)}  {el:5.0f}s ")
            sys.stdout.flush()

            if n == len(missing):
                print("\n\nall present.")
                done_flag.set()
                return True

            stalled_for = 0.0 if n != last_n else stalled_for + poll
            last_n = n

            if not watch and el > per_file_timeout:
                print(f"\n\ngave up after {per_file_timeout:.0f}s with {n} of "
                      f"{len(missing)} arrived.")
                break
            if stalled_for >= 180 and n == 0:
                print("\n\nnothing has arrived in 3 minutes and no bytes are moving.")
                print("OneDrive is not serving these files. Worth checking:")
                print("  - the OneDrive menu-bar icon: is it paused, or asking you to sign in?")
                print("  - Finder: right-click confocal/ and choose "
                      "'Always keep on this device'")
                print("  - whether the folder is shared with you but not yet added to "
                      "your own OneDrive")
                break
            time.sleep(poll)
    except KeyboardInterrupt:
        print("\n\nstopped. Files already downloaded stay downloaded.")
    done_flag.set()
    return False


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="", help="same study config as build_segments.py")
    p.add_argument("--stacks", default="")
    p.add_argument("--z-levels", default="5,9,13,17")
    p.add_argument("--from-grid", action="store_true",
                   help="check the COUNT_field_*_grid.png figures instead")
    p.add_argument("--fields", default="", help="with --from-grid, e.g. 1,2")
    p.add_argument("--fetch", action="store_true", help="actually pull them down")
    p.add_argument("--watch", action="store_true",
                   help="keep waiting until everything has arrived")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--timeout", type=float, default=600,
                   help="seconds to wait before giving up (ignored with --watch)")
    p.add_argument("--poll", type=float, default=2.0)
    args = p.parse_args()
    args.fields = {int(x) for x in args.fields.split(",") if x.strip()}

    if args.config:
        B.apply_config(args.config)

    print("build needs:")
    files = wanted_files(args)
    if not files:
        sys.exit("no files resolved -- check --stacks / --config")

    have, miss = report(files)
    if not miss:
        print("\nready to build.")
        return 0

    if not args.fetch:
        print(f"\n{len(miss)} still to come. Run again with --fetch to request them.")
        return 1

    ok = fetch(files, args.workers, args.timeout, args.watch, args.poll)
    report(files)
    if ok:
        print("\nready to build. Next:")
        if args.from_grid:
            print("  /usr/bin/python3 build_segments.py --from-grid --clean")
        else:
            print(f"  /usr/bin/python3 build_segments.py --z-levels {args.z_levels} "
                  f"--squares-per-field 16 --blocks 20 --replicates 3 --clean")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
