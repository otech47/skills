#!/usr/bin/env python3
"""Measure whether a rendered explainer is in motion or is a narrated slideshow.

usage: check-motion.py VIDEO [--output RESULT.json] [--fps 10]
       [--min-coverage 0.45] [--max-still 2.0] [--max-cuts 0]
       [--visible 0.001] [--level 10] [--cut 24]

The video is decoded at 192x108 gray and sampled at --fps. Each sample is
compared with the previous one pixel by pixel.

changed area   fraction of pixels whose luma moved by more than --level
               between two samples. An interval counts as visible motion when
               that fraction reaches --visible (0.001 is about 2000 pixels of
               a 1080p frame, the size of a moving pointer or a growing bar).
coverage       fraction of intervals with visible motion
dead windows   runs of intervals without visible motion longer than
               --max-still seconds
hard cuts      intervals whose mean luma difference reaches --cut: a swap of
               the whole picture rather than a move. Pushes, lifts and chapter
               boundaries in a continuous explainer do not register as cuts.

Changed area rather than mean difference, so that a small moving element on a
large still frame counts as motion and a slow full-frame glow does not. The
script catches a slideshow; it cannot tell informative motion from decoration,
so inspect the dead windows before trusting a failure, and inspect the stills
before trusting a pass.
"""
import argparse
import json
import subprocess
import sys

WIDTH, HEIGHT = 192, 108


def decode(path, fps):
    command = [
        "ffmpeg", "-v", "error", "-i", path,
        "-vf", f"fps={fps},scale={WIDTH}:{HEIGHT}:flags=area,format=gray",
        "-f", "rawvideo", "-",
    ]
    raw = subprocess.run(command, check=True, capture_output=True).stdout
    size = WIDTH * HEIGHT
    return [raw[i * size:(i + 1) * size] for i in range(len(raw) // size)]


def compare(a, b, level):
    changed = 0
    total = 0
    for x, y in zip(a, b):
        d = abs(x - y)
        total += d
        if d > level:
            changed += 1
    return changed / len(a), total / len(a)


def profile(path, fps, visible, level, cut):
    frames = decode(path, fps)
    pairs = [compare(frames[i - 1], frames[i], level) for i in range(1, len(frames))]
    areas = [area for area, _ in pairs]
    means = [mean for _, mean in pairs]
    moving = [area >= visible for area in areas]
    cuts = [round(i / fps, 2) for i, mean in enumerate(means, start=1) if mean >= cut]
    windows, start = [], None
    for index, m in enumerate(moving + [True]):
        if not m and start is None:
            start = index
        elif m and start is not None:
            windows.append((start / fps, index / fps))
            start = None
    per_second = []
    for s in range(0, len(areas), fps):
        chunk = areas[s:s + fps]
        per_second.append(round(max(chunk), 4) if chunk else 0.0)
    return {
        "video": path,
        "sample_fps": fps,
        "seconds": round(len(frames) / fps, 2),
        "coverage": round(sum(moving) / max(1, len(moving)), 3),
        "longest_still_seconds": round(max((b - a for a, b in windows), default=0.0), 2),
        "hard_cuts": cuts,
        "still_windows": [[round(a, 1), round(b, 1)] for a, b in windows],
        "per_second_max_changed_area": per_second,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--output")
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--visible", type=float, default=0.001, help="changed area fraction that counts as visible motion")
    parser.add_argument("--level", type=int, default=10, help="luma difference that counts a pixel as changed")
    parser.add_argument("--cut", type=float, default=24.0, help="mean luma difference that counts as a hard cut")
    parser.add_argument("--min-coverage", type=float, default=0.45)
    parser.add_argument("--max-still", type=float, default=2.0)
    parser.add_argument("--max-cuts", type=int, default=0)
    args = parser.parse_args()

    result = profile(args.video, args.fps, args.visible, args.level, args.cut)
    dead = [w for w in result["still_windows"] if w[1] - w[0] > args.max_still]
    failures = []
    if result["coverage"] < args.min_coverage:
        failures.append(f"coverage {result['coverage']} is below {args.min_coverage}")
    if dead:
        failures.append(f"{len(dead)} still window(s) longer than {args.max_still}s: " + ", ".join(f"{a}-{b}s" for a, b in dead))
    if len(result["hard_cuts"]) > args.max_cuts:
        failures.append(f"{len(result['hard_cuts'])} hard cut(s) at " + ", ".join(f"{c}s" for c in result["hard_cuts"]))
    result["thresholds"] = {"visible": args.visible, "level": args.level, "cut": args.cut, "min_coverage": args.min_coverage, "max_still": args.max_still, "max_cuts": args.max_cuts}
    result["dead_windows"] = dead
    result["status"] = "fail" if failures else "pass"
    result["failures"] = failures
    if args.output:
        with open(args.output, "w") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    summary = {key: result[key] for key in ("status", "coverage", "longest_still_seconds", "hard_cuts", "dead_windows")}
    print(json.dumps(summary))
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
