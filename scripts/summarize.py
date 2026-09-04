#!/usr/bin/env python3
"""Regenerate the summary tables in README.md straight from the CSV files.

Standard library only. Run from anywhere:

    python scripts/summarize.py
"""

import csv
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSETS = ["nominal_24-28C"]
CLASSES = ["air", "fresh", "early_spoilage", "spoiled"]


def read_subset(path):
    """Yield (filename, list-of-row-dicts) for every CSV in a subset."""
    for name in sorted(os.listdir(path)):
        if not name.endswith(".csv"):
            continue
        with open(os.path.join(path, name), newline="", encoding="utf-8") as fh:
            yield name, list(csv.DictReader(fh))


def implied_baseline_gas(rows):
    """Invert gas_drop_pct = (b - R) / b * 100 to recover b.

    Returns (min, max) over the frames of one recording. Frames with a drop of
    exactly 0 or 100 % are skipped: they carry no information about b.
    """
    vals = []
    for r in rows:
        try:
            drop = float(r["gas_drop_pct"])
            res = float(r["gas_resistance"])
        except (TypeError, ValueError, KeyError):
            continue
        if drop not in (0.0, 100.0):
            vals.append(res / (1.0 - drop / 100.0))
    return (min(vals), max(vals)) if vals else (None, None)


def baseline_src(rows):
    """Pull baseline_src=... out of the note column, if present."""
    for r in rows:
        note = (r.get("note") or "").strip()
        for token in note.split():
            if token.startswith("baseline_src="):
                return token[len("baseline_src="):]
    return "-"


def summarize(subset):
    path = os.path.join(ROOT, "data", subset)
    if not os.path.isdir(path):
        sys.exit("missing subset directory: %s" % path)

    files = 0
    frames = 0
    labels = Counter()
    temps = []
    drops = []
    baselines = []
    per_file = []

    for name, rows in read_subset(path):
        files += 1
        frames += len(rows)
        labels.update(r["time_label"] for r in rows)
        temps += [float(r["temperature"]) for r in rows]
        drops += [float(r["gas_drop_pct"]) for r in rows]
        lo, hi = implied_baseline_gas(rows)
        if lo is not None:
            baselines.append((name, lo, hi, baseline_src(rows)))
        dur = max(float(r["elapsed_s"]) for r in rows) if rows else 0.0
        top = Counter(r["time_label"] for r in rows).most_common(1)[0][0]
        per_file.append((name, len(rows), top, dur))

    print("=" * 72)
    print(subset)
    print("=" * 72)
    print("recordings      : %d" % files)
    print("frames          : %d" % frames)
    print("temperature     : %.1f - %.1f C" % (min(temps), max(temps)))
    print("gas_drop_pct    : %.1f - %.1f %%" % (min(drops), max(drops)))
    print("detection window: %.1f - %.1f s"
          % (min(p[3] for p in per_file), max(p[3] for p in per_file)))
    print()
    print("class distribution (frames):")
    for cls in CLASSES:
        print("  %-16s %5d" % (cls, labels.get(cls, 0)))
    unknown = set(labels) - set(CLASSES)
    for cls in sorted(unknown):
        print("  %-16s %5d   <- unexpected label" % (cls, labels[cls]))
    print()

    distinct = {round(lo) for _, lo, _, _ in baselines}
    print("implied baseline_gas: %d distinct value(s) across %d files"
          % (len(distinct), len(baselines)))
    for val in sorted(distinct):
        n = sum(1 for _, lo, _, _ in baselines if round(lo) == val)
        print("  %9d ohm  (%d file%s)" % (val, n, "" if n == 1 else "s"))
    print()
    print("per file (baseline recovered by inversion; src read from note):")
    print("  %-38s %11s  %8s  %s"
          % ("file", "baseline", "scatter", "src"))
    for name, lo, hi, src in sorted(baselines, key=lambda b: b[1]):
        print("  %-38s %11.1f  %8.1f  %s" % (name, lo, hi - lo, src))
    print()
    return frames, labels


def main():
    totals = Counter()
    grand = 0
    for subset in SUBSETS:
        frames, labels = summarize(subset)
        grand += frames
        totals.update(labels)
    print("=" * 72)
    print("TOTAL: %d frames" % grand)
    for cls in CLASSES:
        print("  %-16s %5d" % (cls, totals.get(cls, 0)))


if __name__ == "__main__":
    main()
