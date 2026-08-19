#!/usr/bin/env bash
# Real entropy for one report's decorative chrome (report-flair): a corner
# badge, a corner mascot, and the accent hue they share. Run this once per
# report, right before you fill in the flair snippet from
# references/flair-chrome.md. Every number below comes from the OS CSPRNG via
# python's random.SystemRandom, not from a hash of the title and not from a
# fixed list, so it cannot be pattern-matched across reports. Prints
# shell-assignable KEY=VALUE lines; read them, do not hand-derive them.
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "roll-flair: python3 not found" >&2; exit 1; }

python3 - <<'PY'
import random
r = random.SystemRandom()

# Hue stays out of the warn (red/orange) and good (green) bands, so a rolled
# color can never be mistaken for the report's semantic warning or success
# color. 170-340 covers teal, cyan, blue, indigo, violet, purple, magenta,
# and pink: wide enough range, still bounded and controlled.
hue = r.randint(170, 340)

badge_radius   = r.randint(16, 20)
badge_dot      = round(r.uniform(3, 6), 1)
badge_rotation = r.choice([0, 45])
badge_stroke   = round(r.uniform(1.2, 2.2), 1)
badge_dash     = r.choice(["none", "3 3", "2 4", "5 2"])
badge_spin_dur = round(r.uniform(18, 40), 1)
badge_spin_dir = r.choice(["normal", "reverse"])
badge_pulse    = round(r.uniform(2.2, 4.0), 1)

masc_rx     = r.randint(17, 21)
masc_ry     = r.randint(14, 18)
eye_dx      = r.randint(5, 8)
eye_dy      = r.randint(18, 24)
eye_r       = round(r.uniform(2.2, 3.4), 1)
mouth_y     = r.randint(32, 40)
blink_dur   = round(r.uniform(3.2, 6.0), 1)
blink_delay = round(r.uniform(0.0, 1.5), 2)
bob_dur     = round(r.uniform(3.0, 6.0), 1)
bob_amp     = round(r.uniform(1.0, 2.2), 1)

for k, v in [
    ("HUE", hue),
    ("BADGE_RADIUS", badge_radius),
    ("BADGE_DOT", badge_dot),
    ("BADGE_ROTATION", badge_rotation),
    ("BADGE_STROKE", badge_stroke),
    ("BADGE_DASH", badge_dash),
    ("BADGE_SPIN_DUR", badge_spin_dur),
    ("BADGE_SPIN_DIR", badge_spin_dir),
    ("BADGE_PULSE", badge_pulse),
    ("MASC_RX", masc_rx),
    ("MASC_RY", masc_ry),
    ("EYE_DX", eye_dx),
    ("EYE_DY", eye_dy),
    ("EYE_R", eye_r),
    ("MOUTH_Y", mouth_y),
    ("BLINK_DUR", blink_dur),
    ("BLINK_DELAY", blink_delay),
    ("BOB_DUR", bob_dur),
    ("BOB_AMP", bob_amp),
]:
    print(f"{k}={v}")
PY
