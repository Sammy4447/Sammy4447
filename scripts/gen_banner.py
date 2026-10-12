#!/usr/bin/env python3
"""Generate an animated LED dot-matrix name banner as an SVG.

Usage: python3 scripts/gen_banner.py "SAMEER BHATT" assets/banner.svg
"""
import random
import sys

# 5x7 dot-matrix glyphs
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}

CELL = 12        # px between dot centres
R = 4.4          # dot radius
MARGIN = 2       # empty dot columns/rows around the text
CYCLE = 14       # seconds per full animation loop
COL_STAGGER = 0.035  # seconds between neighbouring columns (scan + wave)
SPARKLE = 1.5    # spread of random per-dot boot/dissolve times
TWINKLES = 40    # background dots that twinkle

GREEN, WHITE, CYAN = "#39ff14", "#f0fff0", "#00e5ff"

# Timeline (seconds into the loop)
T_SCAN = 2.5     # scanner beam starts
T_WAVE = 5.6     # ripple starts
T_GLITCH = 9.3   # glitch burst
T_OFF = 10.5     # dissolve starts


def pct(t: float) -> str:
    return f"{t / CYCLE * 100:.2f}%"


def build(text: str) -> str:
    rnd = random.Random(text)  # deterministic output for the same text

    # Lay glyphs out into a list of columns of lit rows
    cols = []
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for x in range(len(glyph[0])):
            cols.append({y for y in range(7) if glyph[y][x] == "#"})
        cols.append(set())  # 1-column gap between letters
    cols.pop()

    n_cols = len(cols) + 2 * MARGIN
    n_rows = 7 + 2 * MARGIN
    w, h = n_cols * CELL, n_rows * CELL
    sweep = len(cols) * COL_STAGGER

    def cx(c):
        return (c + 0.5) * CELL

    lit = {(i + MARGIN, r + MARGIN) for i, rows in enumerate(cols) for r in rows}

    # Static background board, a few of its dots twinkle
    blanks = [(c, r) for c in range(n_cols) for r in range(n_rows) if (c, r) not in lit]
    twinkle = set(rnd.sample(blanks, min(TWINKLES, len(blanks))))
    off_dots = []
    for c, r in blanks:
        if (c, r) in twinkle:
            style = f"animation-delay:{rnd.uniform(0, 6):.2f}s;animation-duration:{rnd.uniform(3, 7):.2f}s"
            off_dots.append(f'<circle class="tw" style="{style}" cx="{cx(c)}" cy="{cx(r)}" r="{R}"/>')
        else:
            off_dots.append(f'<circle cx="{cx(c)}" cy="{cx(r)}" r="{R}"/>')

    # Lit dots: one group per column (scan flash + wave), each dot fades in/out at a random time
    lit_groups = []
    for i, rows in enumerate(cols):
        if not rows:
            continue
        c = i + MARGIN
        dots = "".join(
            f'<circle class="d" style="animation-delay:{rnd.uniform(0, SPARKLE):.2f}s" '
            f'cx="{cx(c)}" cy="{cx(r + MARGIN)}" r="{R}"/>'
            for r in sorted(rows)
        )
        lit_groups.append(f'<g class="col" style="animation-delay:{i * COL_STAGGER:.3f}s">{dots}</g>')

    beam_w = 4 * CELL
    css = f"""
  .board {{ fill: #0b0f0b; }}
  .off circle {{ fill: #13241a; }}
  .tw {{ animation: twinkle 5s ease-in-out infinite; }}
  .text {{ filter: url(#glow); animation: glitch {CYCLE}s steps(1) infinite;
           transform-box: fill-box; transform-origin: center; }}
  .col {{ fill: {GREEN}; animation: col {CYCLE}s ease-in-out infinite; }}
  .d {{ opacity: 0.05; animation: dot {CYCLE}s linear infinite; }}
  .beam {{ opacity: 0; animation: beam {CYCLE}s linear infinite; }}

  /* random sparkle boot, flicker, random dissolve */
  @keyframes dot {{
    0% {{ opacity: 0.05; }}
    {pct(0.15)} {{ opacity: 1; }}
    {pct(0.25)} {{ opacity: 0.35; }}
    {pct(0.35)} {{ opacity: 1; }}
    {pct(T_OFF)} {{ opacity: 1; }}
    {pct(T_OFF + 0.12)} {{ opacity: 0.6; }}
    {pct(T_OFF + 0.2)} {{ opacity: 1; }}
    {pct(T_OFF + 0.35)} {{ opacity: 0.05; }}
    100% {{ opacity: 0.05; }}
  }}

  /* scanner flash, then a cyan ripple travelling left to right */
  @keyframes col {{
    0% {{ fill: {GREEN}; transform: translateY(0); }}
    {pct(T_SCAN)} {{ fill: {GREEN}; }}
    {pct(T_SCAN + 0.1)} {{ fill: {WHITE}; }}
    {pct(T_SCAN + 0.4)} {{ fill: {GREEN}; }}
    {pct(T_WAVE)} {{ fill: {GREEN}; transform: translateY(0); }}
    {pct(T_WAVE + 0.35)} {{ fill: {CYAN}; transform: translateY(-{CELL}px); }}
    {pct(T_WAVE + 0.7)} {{ fill: {GREEN}; transform: translateY(3px); }}
    {pct(T_WAVE + 0.9)} {{ transform: translateY(0); }}
    100% {{ fill: {GREEN}; transform: translateY(0); }}
  }}

  /* light beam that rides along with the scanner flash */
  @keyframes beam {{
    0% {{ opacity: 0; transform: translateX(-{beam_w}px); }}
    {pct(T_SCAN - 0.01)} {{ opacity: 0; transform: translateX(-{beam_w}px); }}
    {pct(T_SCAN)} {{ opacity: 1; transform: translateX({MARGIN * CELL - beam_w / 2}px); }}
    {pct(T_SCAN + sweep)} {{ opacity: 1; transform: translateX({w - MARGIN * CELL - beam_w / 2}px); }}
    {pct(T_SCAN + sweep + 0.3)} {{ opacity: 0; transform: translateX({w}px); }}
    100% {{ opacity: 0; transform: translateX({w}px); }}
  }}

  /* short broken-signal jitter */
  @keyframes glitch {{
    0% {{ transform: none; }}
    {pct(T_GLITCH)} {{ transform: translate(6px, -2px) skewX(-12deg); }}
    {pct(T_GLITCH + 0.08)} {{ transform: translate(-8px, 1px) skewX(8deg); }}
    {pct(T_GLITCH + 0.16)} {{ transform: translate(3px, 0) scaleY(0.85); }}
    {pct(T_GLITCH + 0.24)} {{ transform: translate(-4px, 2px); }}
    {pct(T_GLITCH + 0.32)} {{ transform: none; }}
    {pct(T_GLITCH + 0.6)} {{ transform: translate(5px, 0) skewX(-6deg); }}
    {pct(T_GLITCH + 0.66)} {{ transform: none; }}
    100% {{ transform: none; }}
  }}

  @keyframes twinkle {{
    0%, 70%, 100% {{ fill: #13241a; }}
    80% {{ fill: #2a6b3a; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    .text, .col, .d, .beam, .tw {{ animation: none; }}
    .d {{ opacity: 1; }}
  }}
"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{text}">
<title>{text}</title>
<style>{css}</style>
<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="beamGrad" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{WHITE}" stop-opacity="0.22"/>
    <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="boardClip"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<rect class="board" width="{w}" height="{h}" rx="14"/>
<g class="off">{"".join(off_dots)}</g>
<g clip-path="url(#boardClip)"><rect class="beam" width="{beam_w}" height="{h}" fill="url(#beamGrad)"/></g>
<g class="text">{"".join(lit_groups)}</g>
</svg>
"""


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "SAMEER BHATT"
    out = sys.argv[2] if len(sys.argv) > 2 else "assets/banner.svg"
    with open(out, "w") as f:
        f.write(build(text))
    print(f"wrote {out}")
