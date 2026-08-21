#!/usr/bin/env python3
"""Rolls and applies one report's decorative chrome. See references/flair-chrome.md."""

import math
import random
import re
import sys

r = random.SystemRandom()

LIGHT_BG = (251, 251, 250)
DARK_BG = (22, 22, 26)


def hsl_to_rgb(h, s, l):
    h, s, l = h / 360.0, s / 100.0, l / 100.0
    if s == 0:
        v = int(round(l * 255))
        return (v, v, v)

    def hue2rgb(p, q, t):
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return tuple(int(round(hue2rgb(p, q, h + o) * 255)) for o in (1 / 3, 0, -1 / 3))


def rel_lum(rgb):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


# Purple through pink spans far more degrees than teal or cyan, so sampling hue
# uniformly makes most reports come out violet. Pick a band first, then a hue in it.
HUE_BANDS = [(168, 184), (184, 198), (198, 212), (212, 230), (230, 248),
             (248, 264), (264, 282), (282, 298), (298, 314), (314, 338)]


def _hue():
    lo, hi = r.choice(HUE_BANDS)
    return r.randint(lo, hi)


def _fit(h, s, start, bg, target, step):
    """Cyan must be far darker than violet to pass on white, so reject-and-retry
    would silently drop whole hue bands. Adjust the sample, never discard it."""
    l = start
    while 14 <= l <= 94:
        if contrast(hsl_to_rgb(h, s, l), bg) >= target:
            return l
        l += step
    return None


def roll_colors():
    """Stays out of the warn (red/orange) and good (green) bands, so a decorative
    color is never mistaken for a semantic one. Guarantees 4.5:1 on both backgrounds."""
    while True:
        h1 = _hue()
        s_l, s_d = r.randint(52, 95), r.randint(62, 100)
        l_l = _fit(h1, s_l, r.randint(32, 52), LIGHT_BG, 4.5, -1)
        l_d = _fit(h1, s_d, r.randint(60, 80), DARK_BG, 4.5, 1)
        if l_l is not None and l_d is not None:
            break
    while True:
        h2 = _hue()
        if min(abs(h2 - h1), 360 - abs(h2 - h1)) >= 55:
            break
    s2_l, s2_d = r.randint(55, 95), r.randint(65, 100)
    l2_l = _fit(h2, s2_l, r.randint(36, 56), LIGHT_BG, 3.0, -1) or 40
    l2_d = _fit(h2, s2_d, r.randint(58, 80), DARK_BG, 3.0, 1) or 70
    return {
        "light": (
            f"hsl({h1} {s_l}% {l_l}%)",
            f"hsl({h1} {r.randint(60, 85)}% {r.randint(93, 96)}%)",
            f"hsl({h2} {s2_l}% {l2_l}%)",
        ),
        "dark": (
            f"hsl({h1} {s_d}% {l_d}%)",
            f"hsl({h1} {r.randint(28, 46)}% {r.randint(17, 24)}%)",
            f"hsl({h2} {s2_d}% {l2_d}%)",
        ),
    }


C = 24.0


def poly(cx, cy, rad, n, rot=0.0):
    pts = []
    for i in range(n):
        a = math.radians(rot - 90 + i * 360.0 / n)
        pts.append(f"{cx + rad * math.cos(a):.2f},{cy + rad * math.sin(a):.2f}")
    return " ".join(pts)


def star(cx, cy, r_out, r_in, n, rot=0.0):
    pts = []
    for i in range(n * 2):
        rad = r_out if i % 2 == 0 else r_in
        a = math.radians(rot - 90 + i * 180.0 / n)
        pts.append(f"{cx + rad * math.cos(a):.2f},{cy + rad * math.sin(a):.2f}")
    return " ".join(pts)


def shape_svg(kind, cx, cy, size, rot, fill, stroke, sw, anim=""):
    """Every branch must return exactly one element; callers wrap the result."""
    style = f'{anim}fill:{fill};stroke:{stroke};stroke-width:{sw}'
    common = f'style="{style}"'
    if kind == "circle":
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{size:.2f}" {common}/>'
    if kind == "ring":
        return (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{size:.2f}" '
                f'style="{anim}fill:none;stroke:{stroke};stroke-width:{sw}"/>')
    if kind == "square":
        return (f'<rect x="{cx - size:.2f}" y="{cy - size:.2f}" width="{2 * size:.2f}" '
                f'height="{2 * size:.2f}" rx="{min(1.5, size / 3):.2f}" '
                f'transform="rotate({rot:.1f} {cx:.2f} {cy:.2f})" {common}/>')
    if kind.startswith("poly"):
        n = int(kind[4:])
        return f'<polygon points="{poly(cx, cy, size, n, rot)}" {common}/>'
    if kind.startswith("star"):
        n = int(kind[4:])
        inner = size * r.uniform(0.38, 0.55)
        return f'<polygon points="{star(cx, cy, size, inner, n, rot)}" {common}/>'
    if kind == "cross":
        t = size * 0.3
        return (f'<path d="M{cx - t:.2f},{cy - size:.2f} h{2 * t:.2f} v{size - t:.2f} '
                f'h{size - t:.2f} v{2 * t:.2f} h{-(size - t):.2f} v{size - t:.2f} '
                f'h{-2 * t:.2f} v{-(size - t):.2f} h{-(size - t):.2f} v{-2 * t:.2f} '
                f'h{size - t:.2f} z" transform="rotate({rot:.1f} {cx:.2f} {cy:.2f})" {common}/>')
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{size:.2f}" {common}/>'


SAT_SHAPES = ["circle", "square", "poly3", "poly4", "poly6", "star4", "star5", "ring", "cross"]
CORE_SHAPES = ["circle", "ring", "square", "poly3", "poly5", "poly6", "poly8",
               "star4", "star5", "star6", "cross", "none"]


def build_ornament():
    """Rolls the composition itself, not just the numbers in a fixed one. Keep it
    that way; a fixed layout with jittered values is recognizable after a few reports."""
    parts = []
    fill_a, fill_b = "var(--accent)", "var(--flair2)"
    soft = "var(--accent-soft)"

    n_rings = r.choice([1, 1, 2, 2, 3])
    radii = r.sample([9.5, 12.5, 15.5, 18.0, 20.5], n_rings)
    for rad in sorted(radii):
        col = r.choice([fill_a, fill_a, fill_b])
        sw = round(r.uniform(1.0, 2.4), 1)
        dur = round(r.uniform(14, 46), 1)
        direction = r.choice(["normal", "reverse"])
        op = round(r.uniform(0.55, 1.0), 2)
        anim = (f'transform-box:fill-box;transform-origin:center;'
                f'animation:flspin {dur}s linear infinite {direction};opacity:{op}')
        if r.random() < 0.35:
            sweep = r.uniform(90, 280)
            a0 = r.uniform(0, 360)
            a1 = a0 + sweep
            x0, y0 = C + rad * math.cos(math.radians(a0)), C + rad * math.sin(math.radians(a0))
            x1, y1 = C + rad * math.cos(math.radians(a1)), C + rad * math.sin(math.radians(a1))
            large = 1 if sweep > 180 else 0
            parts.append(
                f'<path d="M{x0:.2f},{y0:.2f} A{rad:.2f},{rad:.2f} 0 {large} 1 {x1:.2f},{y1:.2f}" '
                f'style="fill:none;stroke:{col};stroke-width:{sw};stroke-linecap:round;{anim}"/>')
        else:
            dash = r.choice(["none", "2 4", "3 3", "5 2", "6 3", "1 3", "8 4"])
            parts.append(
                f'<circle cx="{C}" cy="{C}" r="{rad:.2f}" '
                f'style="fill:none;stroke:{col};stroke-width:{sw};stroke-dasharray:{dash};{anim}"/>')

    core = r.choice(CORE_SHAPES)
    if core != "none":
        size = round(r.uniform(4.0, 8.5), 1)
        rot = round(r.uniform(0, 360), 1)
        filled = r.random()
        fill = soft if filled < 0.55 else ("none" if filled < 0.75 else fill_b)
        stroke = r.choice([fill_a, fill_a, fill_b])
        sw = round(r.uniform(1.2, 2.0), 1)
        anims = []
        if r.random() < 0.75:
            anims.append(f'flpulse {round(r.uniform(2.0, 5.0), 1)}s ease-in-out infinite')
        if r.random() < 0.45:
            anims.append(f'flspin {round(r.uniform(8, 30), 1)}s linear infinite '
                         f'{r.choice(["normal", "reverse"])}')
        anim = ""
        if anims:
            anim = ('transform-box:fill-box;transform-origin:center;'
                    f'animation:{",".join(anims)};')
        parts.append(shape_svg(core, C, C, size, rot, fill, stroke, sw, anim))

    n_sat = r.choice([0, 2, 3, 3, 4, 5, 6])
    if n_sat:
        orbit_r = round(r.uniform(13.0, 20.5), 1)
        even = r.random() < 0.6
        base = r.uniform(0, 360)
        sat_dur = round(r.uniform(16, 50), 1)
        sat_dir = r.choice(["normal", "reverse"])
        inner = []
        for i in range(n_sat):
            ang = base + (i * 360.0 / n_sat if even else r.uniform(0, 360))
            rad = orbit_r if even else orbit_r * r.uniform(0.75, 1.12)
            sx = C + rad * math.cos(math.radians(ang))
            sy = C + rad * math.sin(math.radians(ang))
            kind = r.choice(SAT_SHAPES)
            size = round(r.uniform(1.3, 3.0), 1)
            col = r.choice([fill_a, fill_a, fill_b])
            tw = (f'transform-box:fill-box;transform-origin:center;'
                  f'animation:fltwinkle {round(r.uniform(1.3, 3.4), 1)}s ease-in-out infinite;'
                  f'animation-delay:{round(r.uniform(0, 2.4), 2)}s;')
            inner.append(shape_svg(kind, sx, sy, size, r.uniform(0, 360),
                                   "none" if kind == "ring" else col, col,
                                   round(r.uniform(0.9, 1.6), 1), tw))
        parts.append(
            f'<g style="transform-box:view-box;transform-origin:{C}px {C}px;'
            f'animation:flspin {sat_dur}s linear infinite {sat_dir}">'
            + "".join(inner) + '</g>')

    bob_dur = round(r.uniform(3.0, 7.0), 1)
    bob_amp = round(r.uniform(1.0, 2.6), 1)
    body = "\n  ".join(parts)
    return (f'<svg class="flair-mark" viewBox="0 0 48 48" role="presentation" '
            f'style="animation:flbob {bob_dur}s ease-in-out infinite">\n  {body}\n</svg>'), bob_amp


QUOTES = [
    ("The good thing about science is that it's true whether or not you believe in it.", "neil degrasse tyson"),
    ("Nothing in life is to be feared, it is only to be understood.", "marie curie"),
    ("I have no special talent. I am only passionately curious.", "albert einstein"),
    ("Extraordinary claims require extraordinary evidence.", "carl sagan"),
    ("We are made of star-stuff.", "carl sagan"),
    ("Science is a way of thinking much more than it is a body of knowledge.", "carl sagan"),
    ("If I have seen further it is by standing on the shoulders of giants.", "isaac newton"),
    ("What I cannot create, I do not understand.", "richard feynman"),
    ("The first principle is that you must not fool yourself, and you are the easiest person to fool.", "richard feynman"),
    ("In mathematics you don't understand things. You just get used to them.", "john von neumann"),
    ("Mathematics is the art of giving the same name to different things.", "henri poincare"),
    ("The purpose of computing is insight, not numbers.", "richard hamming"),
    ("Premature optimization is the root of all evil.", "donald knuth"),
    ("Beware of bugs in the above code; I have only proved it correct, not tried it.", "donald knuth"),
    ("Simplicity is prerequisite for reliability.", "edsger dijkstra"),
    ("Testing shows the presence, not the absence of bugs.", "edsger dijkstra"),
    ("There are only two hard things in computer science: cache invalidation and naming things.", "phil karlton"),
    ("Any sufficiently advanced technology is indistinguishable from magic.", "arthur c. clarke"),
    ("The best way to predict the future is to invent it.", "alan kay"),
    ("Talk is cheap. Show me the code.", "linus torvalds"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "abelson and sussman"),
    ("Make it work, make it right, make it fast.", "kent beck"),
    ("Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away.", "antoine de saint-exupery"),
    ("The unexamined life is not worth living.", "socrates"),
    ("Whereof one cannot speak, thereof one must be silent.", "ludwig wittgenstein"),
    ("The limits of my language mean the limits of my world.", "ludwig wittgenstein"),
    ("He who has a why to live can bear almost any how.", "friedrich nietzsche"),
    ("Man is condemned to be free.", "jean-paul sartre"),
    ("Hell is other people.", "jean-paul sartre"),
    ("One must imagine Sisyphus happy.", "albert camus"),
    ("In the depth of winter, I finally learned that within me there lay an invincible summer.", "albert camus"),
    ("The medium is the message.", "marshall mcluhan"),
    ("Not everything that is faced can be changed, but nothing can be changed until it is faced.", "james baldwin"),
    ("The most beautiful thing we can experience is the mysterious.", "albert einstein"),
    ("Do not go gentle into that good night.", "dylan thomas"),
    ("I would prefer not to.", "herman melville"),
    ("It is not down in any map; true places never are.", "herman melville"),
    ("So it goes.", "kurt vonnegut"),
    ("Everything was beautiful and nothing hurt.", "kurt vonnegut"),
    ("We are what we pretend to be, so we must be careful about what we pretend to be.", "kurt vonnegut"),
    ("The past is never dead. It's not even past.", "william faulkner"),
    ("The world breaks everyone, and afterward, many are strong at the broken places.", "ernest hemingway"),
    ("All you have to do is write one true sentence.", "ernest hemingway"),
    ("Beauty is truth, truth beauty.", "john keats"),
    ("Tell all the truth but tell it slant.", "emily dickinson"),
    ("I dwell in possibility.", "emily dickinson"),
    ("Hope is the thing with feathers.", "emily dickinson"),
    ("Do I contradict myself? Very well then I contradict myself, I am large, I contain multitudes.", "walt whitman"),
    ("The road to hell is paved with adverbs.", "stephen king"),
    ("Not all those who wander are lost.", "j.r.r. tolkien"),
    ("All we have to decide is what to do with the time that is given us.", "j.r.r. tolkien"),
    ("The best way out is always through.", "robert frost"),
    ("Two roads diverged in a wood, and I took the one less traveled by.", "robert frost"),
    ("The impediment to action advances action. What stands in the way becomes the way.", "marcus aurelius"),
    ("You have power over your mind, not outside events. Realize this, and you will find strength.", "marcus aurelius"),
    ("We suffer more often in imagination than in reality.", "seneca"),
    ("It is not that we have a short time to live, but that we waste a lot of it.", "seneca"),
    ("I have made this longer than usual because I have not had time to make it shorter.", "blaise pascal"),
    ("All of humanity's problems stem from man's inability to sit quietly in a room alone.", "blaise pascal"),
    ("The heart has its reasons which reason knows nothing of.", "blaise pascal"),
    ("Every child is an artist. The problem is how to remain an artist once we grow up.", "pablo picasso"),
    ("I am always doing that which I cannot do, in order that I may learn how to do it.", "pablo picasso"),
    ("Art is the lie that enables us to realize the truth.", "pablo picasso"),
    ("I dream my painting and I paint my dream.", "vincent van gogh"),
    ("If you hear a voice within you say you cannot paint, then by all means paint, and that voice will be silenced.", "vincent van gogh"),
    ("Great things are done by a series of small things brought together.", "vincent van gogh"),
    ("Creativity takes courage.", "henri matisse"),
    ("Do not fear mistakes. There are none.", "miles davis"),
    ("Don't play what's there, play what's not there.", "miles davis"),
    ("If you're not making a mistake, it's a mistake.", "miles davis"),
    ("Nothing is more revealing than movement.", "martha graham"),
    ("The body says what words cannot.", "martha graham"),
    ("I paint flowers so they will not die.", "frida kahlo"),
    ("Feet, what do I need you for when I have wings to fly?", "frida kahlo"),
    ("I am my own muse, the subject I know best.", "frida kahlo"),
    ("I have failed over and over and over again in my life. And that is why I succeed.", "michael jordan"),
    ("You miss 100% of the shots you don't take.", "wayne gretzky"),
    ("Float like a butterfly, sting like a bee.", "muhammad ali"),
    ("It ain't over till it's over.", "yogi berra"),
    ("When you come to a fork in the road, take it.", "yogi berra"),
    ("In theory there is no difference between theory and practice. In practice there is.", "yogi berra"),
    ("The more I practice, the luckier I get.", "gary player"),
    ("Pressure is a privilege.", "billie jean king"),
    ("Champions keep playing until they get it right.", "billie jean king"),
    ("Injustice anywhere is a threat to justice everywhere.", "martin luther king jr."),
    ("The arc of the moral universe is long, but it bends toward justice.", "martin luther king jr."),
    ("Darkness cannot drive out darkness; only light can do that.", "martin luther king jr."),
    ("Education is the most powerful weapon which you can use to change the world.", "nelson mandela"),
    ("It always seems impossible until it's done.", "nelson mandela"),
    ("I learned that courage was not the absence of fear, but the triumph over it.", "nelson mandela"),
    ("The best way to find yourself is to lose yourself in the service of others.", "mahatma gandhi"),
    ("Well-behaved women seldom make history.", "laurel thatcher ulrich"),
    ("If they don't give you a seat at the table, bring a folding chair.", "shirley chisholm"),
    ("I am no bird; and no net ensnares me.", "charlotte bronte"),
    ("You may not control all the events that happen to you, but you can decide not to be reduced by them.", "maya angelou"),
    ("There is no greater agony than bearing an untold story inside you.", "maya angelou"),
    ("People will forget what you said, but people will never forget how you made them feel.", "maya angelou"),
    ("If you don't like something, change it. If you can't change it, change your attitude.", "maya angelou"),
    ("The most common way people give up their power is by thinking they don't have any.", "alice walker"),
    ("Speak your mind, even if your voice shakes.", "maggie kuhn"),
    ("One child, one teacher, one book, one pen can change the world.", "malala yousafzai"),
    ("Design is not just what it looks like and feels like. Design is how it works.", "steve jobs"),
    ("Stay hungry. Stay foolish.", "steve jobs"),
    ("Real artists ship.", "steve jobs"),
    ("Good design is as little design as possible.", "dieter rams"),
    ("Less, but better.", "dieter rams"),
    ("The details are not the details. They make the design.", "charles eames"),
    ("Take your pleasure seriously.", "charles eames"),
    ("If you think good design is expensive, you should look at the cost of bad design.", "ralf speth"),
    ("The journey of a thousand miles begins with a single step.", "lao tzu"),
    ("Nature does not hurry, yet everything is accomplished.", "lao tzu"),
    ("When I let go of what I am, I become what I might be.", "lao tzu"),
    ("It does not matter how slowly you go as long as you do not stop.", "confucius"),
    ("The man who moves a mountain begins by carrying away small stones.", "confucius"),
    ("Everything has beauty, but not everyone sees it.", "confucius"),
    ("Our greatest glory is not in never falling, but in rising every time we fall.", "confucius"),
    ("We are all in the gutter, but some of us are looking at the stars.", "oscar wilde"),
    ("I can resist everything except temptation.", "oscar wilde"),
    ("The only way to get rid of a temptation is to yield to it.", "oscar wilde"),
    ("Clothes make the man. Naked people have little or no influence on society.", "mark twain"),
    ("Whenever you find yourself on the side of the majority, it is time to pause and reflect.", "mark twain"),
    ("I love deadlines. I love the whooshing noise they make as they go by.", "douglas adams"),
    ("Time is an illusion. Lunchtime doubly so.", "douglas adams"),
    ("A common mistake that people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools.", "douglas adams"),
    ("The ships hung in the sky in much the same way that bricks don't.", "douglas adams"),
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "will durant"),
    ("Fall seven times, stand up eight.", "japanese proverb"),
    ("The best time to plant a tree was twenty years ago. The second best time is now.", "proverb"),
]


# An agent asked to "pick a famous quote" returns the same thirty every time, so
# letting it choose freely gives less spread than a uniform draw from QUOTES, not
# more. Rolling a constraint here supplies the entropy the agent lacks; the agent
# supplies the range the pool lacks. Wire it up with --brief and --quote/--author.
DISCIPLINES = [
    "physicist", "mathematician", "poet", "novelist", "playwright", "philosopher",
    "composer", "jazz musician", "painter", "sculptor", "architect", "choreographer",
    "film director", "photographer", "biologist", "chemist", "astronomer",
    "economist", "historian", "anthropologist", "civil rights organizer",
    "labor organizer", "chess player", "athlete", "coach", "comedian", "essayist",
    "translator", "naturalist", "engineer", "aviator", "explorer", "physician",
    "psychologist", "linguist", "war correspondent", "cryptographer", "potter",
    "printmaker", "textile artist", "cartographer", "botanist", "diarist",
]
ERAS = [
    "ancient", "medieval", "renaissance", "17th century", "18th century",
    "19th century", "early 20th century", "mid 20th century", "late 20th century",
    "21st century",
]
REGIONS = [
    "west africa", "south asia", "east asia", "latin america", "the middle east",
    "eastern europe", "the nordic countries", "the caribbean", "southeast asia",
    "indigenous north america", "southern europe", "the british isles",
]
THEMES = [
    "doubt", "craft", "failure", "patience", "curiosity", "solitude",
    "collaboration", "time", "attention", "beginnings", "endings", "constraint",
    "improvisation", "courage", "humility", "obsession", "luck", "revision",
]


def brief():
    who = f"{r.choice(ERAS)} {r.choice(DISCIPLINES)}"
    if r.random() < 0.45:
        who += f" from {r.choice(REGIONS)}"
    return f"a real, correctly attributed line from {who}, on {r.choice(THEMES)}"


def build(quote=None, author=None):
    cols = roll_colors()
    la, ls, l2 = cols["light"]
    da, ds, d2 = cols["dark"]
    svg, bob_amp = build_ornament()
    if not (quote and author):
        quote, author = r.choice(QUOTES)

    css = f"""<style id="flair">
  :root {{ --accent: {la}; --accent-soft: {ls}; --flair2: {l2}; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --accent: {da}; --accent-soft: {ds}; --flair2: {d2}; }}
  }}
  .flair-mark {{ position: fixed; top: 14px; right: 14px; width: 52px; height: 52px; pointer-events: none; z-index: 5; contain: strict; }}
  @keyframes flspin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes flpulse {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: .55; transform: scale(.82); }} }}
  @keyframes fltwinkle {{ 0%, 100% {{ opacity: .18; transform: scale(.65); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}
  @keyframes flbob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-{bob_amp}px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .flair-mark, .flair-mark * {{ animation: none !important; }} }}
  .colophon {{ display: flex; flex-direction: column; align-items: center; gap: .3rem; margin: 2.6rem 0 0; opacity: .8; text-align: center; }}
  .colophon .mark {{ color: var(--ink-soft); font-size: .85rem; font-style: italic; max-width: 34rem; margin: 0; }}
  .colophon .attrib {{ color: var(--ink-faint); font-size: .75rem; margin: 0; }}
</style>"""

    fav = ('<link rel="icon" data-flair href="data:image/svg+xml,'
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           f"%3Ccircle cx='16' cy='16' r='14' fill='{la.replace(' ', ',').replace('%', '%25')}'/%3E"
           "%3Ccircle cx='16' cy='16' r='5' fill='white'/%3E%3C/svg%3E\">")

    colophon = f"""  <div class="colophon">
    <svg width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="2" width="14" height="14" rx="3" transform="rotate(45 9 9)" style="fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.5"></rect></svg>
    <p class="mark">"{quote}"</p>
    <p class="attrib">{author}</p>
  </div>"""

    return css, fav, svg, colophon, quote, author


def strip_flair(html):
    """Each pattern eats exactly the newlines apply_to adds. Change one side and
    repeated apply/strip cycles start growing blank lines."""
    html = re.sub(r'[ \t]*<link rel="icon" data-flair[^>]*>\n?', "", html)
    html = re.sub(r'[ \t]*<style id="flair">.*?</style>\n?', "", html, flags=re.S)
    html = re.sub(r'\n[ \t]*<svg class="flair-mark".*?</svg>', "", html, flags=re.S)
    html = re.sub(r'[ \t]*<div class="colophon">.*?</div>[ \t]*\n', "", html, flags=re.S)
    return html


def apply_to(path, quote=None, author=None):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    html = strip_flair(html)
    css, fav, svg, colophon, quote, author = build(quote, author)

    if "</head>" not in html or "</main>" not in html:
        sys.exit(f"roll-flair: {path} has no </head> or </main>, not a report")

    html = html.replace("</head>", f"{fav}\n{css}\n</head>", 1)
    m = re.search(r"<body[^>]*>", html)
    if not m:
        sys.exit(f"roll-flair: {path} has no <body>")
    html = html[:m.end()] + "\n" + svg + html[m.end():]
    i = html.rfind("</main>")
    html = html[:i] + colophon + "\n" + html[i:]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f'flair applied: {path}\n  quote: "{quote}" / {author}')


def _opt(args, name):
    if name in args:
        i = args.index(name)
        if i + 1 >= len(args):
            sys.exit(f"roll-flair: {name} needs a value")
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return None


if __name__ == "__main__":
    args = sys.argv[1:]
    q = _opt(args, "--quote")
    a = _opt(args, "--author")
    if bool(q) != bool(a):
        sys.exit("roll-flair: --quote and --author go together")

    if args and args[0] == "--brief":
        print(brief())
    elif args and args[0] == "--apply":
        if len(args) != 2:
            sys.exit("usage: roll-flair.sh --apply <report.html> [--quote Q --author A]")
        apply_to(args[1], q, a)
    elif args and args[0] == "--strip":
        if len(args) != 2:
            sys.exit("usage: roll-flair.sh --strip <report.html>")
        with open(args[1], encoding="utf-8") as fh:
            out = strip_flair(fh.read())
        with open(args[1], "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"flair stripped: {args[1]}")
    else:
        css, fav, svg, colophon, quote, author = build(q, a)
        print(fav)
        print(css)
        print(svg)
        print(colophon)
