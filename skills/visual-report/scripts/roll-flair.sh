#!/usr/bin/env bash
# Rolls decorative-chrome parameters from the OS CSPRNG (random.SystemRandom),
# not a hash or a fixed list, so results can't be pattern-matched across reports.
# Run once per report; see references/flair-chrome.md for how the output is used.
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "roll-flair: python3 not found" >&2; exit 1; }

python3 - <<'PY'
import random
r = random.SystemRandom()

# Keep hue out of the warn (red/orange) and good (green) bands, so a rolled
# color can't be mistaken for those semantic colors.
hue = r.randint(170, 340)

ring_stroke   = round(r.uniform(1.3, 2.2), 1)
ring_dash     = r.choice(["none", "3 3", "2 4", "5 2", "6 3"])
ring_spin_dur = round(r.uniform(18, 42), 1)
ring_spin_dir = r.choice(["normal", "reverse"])

gem_half      = r.randint(7, 10)
gem_x         = 24 - gem_half
gem_wh        = 2 * gem_half
gem_pulse_dur = round(r.uniform(2.2, 4.2), 1)

spark_rot     = r.randint(0, 359)
spark1_dur, spark1_delay = round(r.uniform(1.4, 3.0), 1), round(r.uniform(0, 2.0), 2)
spark2_dur, spark2_delay = round(r.uniform(1.4, 3.0), 1), round(r.uniform(0, 2.0), 2)
spark3_dur, spark3_delay = round(r.uniform(1.4, 3.0), 1), round(r.uniform(0, 2.0), 2)

bob_dur = round(r.uniform(3.0, 6.0), 1)
bob_amp = round(r.uniform(1.0, 2.4), 1)

for k, v in [
    ("HUE", hue),
    ("RING_STROKE", ring_stroke),
    ("RING_DASH", ring_dash),
    ("RING_SPIN_DUR", ring_spin_dur),
    ("RING_SPIN_DIR", ring_spin_dir),
    ("GEM_X", gem_x),
    ("GEM_WH", gem_wh),
    ("GEM_PULSE_DUR", gem_pulse_dur),
    ("SPARK_ROT", spark_rot),
    ("SPARK1_DUR", spark1_dur),
    ("SPARK1_DELAY", spark1_delay),
    ("SPARK2_DUR", spark2_dur),
    ("SPARK2_DELAY", spark2_delay),
    ("SPARK3_DUR", spark3_dur),
    ("SPARK3_DELAY", spark3_delay),
    ("BOB_DUR", bob_dur),
    ("BOB_AMP", bob_amp),
]:
    print(f"{k}={v}")
PY
