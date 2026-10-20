"""Tiny pixel-art SVG toolkit used to build the profile graphics.

Everything is drawn from rectangles (a 5x7 bitmap font, notched "pixel" cards,
Bayer-dithered glows) so the SVGs render identically on GitHub without needing
any web fonts, and they match the look of bransonbailey.github.io.
"""

# --- palette (taken from the portfolio's style.css) -------------------------
BG = "#0a0a0a"
FG = "#e0e0e0"
MUTED = "#7a7a7a"      # rgba(224,224,224,.5) on the panel colour
FAINT = "#5b5b5b"      # rgba(224,224,224,.35) on the panel colour
PANEL = "#141414"
BORDER = "#3a3a3a"
RULE = "#1e1e1e"
ACCENT = "#5c8a8a"
ACCENT_HI = "#8abeb7"
BLUE = "#2e5c8a"
BLUE_HI = "#5c8aae"
GOLD = "#ffd700"
PURPLE = "#8b5a8c"
GREEN = "#a1c659"
RED = "#c43e1c"

# --- 5x7 bitmap font ---------------------------------------------------------
_RAW = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.###.",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.",
    "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": ".###.|#...#|....#|..##.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    " ": ".....|.....|.....|.....|.....|.....|.....",
    ".": ".....|.....|.....|.....|.....|.##..|.##..",
    ",": ".....|.....|.....|.....|.##..|..#..|.#...",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    "-": ".....|.....|.....|#####|.....|.....|.....",
    "_": ".....|.....|.....|.....|.....|.....|#####",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "%": "##..#|##..#|...#.|..#..|.#...|#..##|#..##",
    ">": "#....|.#...|..#..|...#.|..#..|.#...|#....",
    "<": "....#|...#.|..#..|.#...|..#..|...#.|....#",
    "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...",
    "@": ".###.|#...#|#.###|#.#.#|#.###|#....|.###.",
    "'": "..#..|..#..|.....|.....|.....|.....|.....",
    "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "=": ".....|.....|#####|.....|#####|.....|.....",
    "*": ".....|#.#.#|.###.|#####|.###.|#.#.#|.....",
    "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#",
    "#": ".#.#.|#####|.#.#.|.#.#.|.#.#.|#####|.#.#.",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "|": "..#..|..#..|..#..|..#..|..#..|..#..|..#..",
    "`": ".#...|..#..|.....|.....|.....|.....|.....",
}
FONT = {k: v.split("|") for k, v in _RAW.items()}
for _k, _rows in FONT.items():
    assert len(_rows) == 7 and all(len(r) == 5 for r in _rows), _k


def text_width(s, scale, ls=0):
    """Pixel width of `s` (advance = 5 px glyph + 1 px gap, per scale unit)."""
    return max(0, len(s) * (6 * scale + ls) - (scale + ls))


def text_d(s, x, y, scale, ls=0):
    """Path data (`d`) drawing `s` with its top-left corner at (x, y)."""
    parts = []
    cx = x
    for ch in s.upper():
        rows = FONT.get(ch, FONT[" "])
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    parts.append(
                        f"M{cx + start * scale} {y + r * scale}h{(c - start) * scale}v{scale}h-{(c - start) * scale}z"
                    )
                else:
                    c += 1
        cx += 6 * scale + ls
    return "".join(parts)


def text(s, x, y, scale, fill, anchor="start", ls=0, extra=""):
    """A <path> element rendering `s`. anchor: start | middle | end."""
    w = text_width(s, scale, ls)
    if anchor == "middle":
        x = x - w // 2
    elif anchor == "end":
        x = x - w
    return f'<path d="{text_d(s, int(x), int(y), scale, ls)}" fill="{fill}" {extra}/>'


# --- shapes ------------------------------------------------------------------
def notch_d(x, y, w, h, n=4):
    """Pixel-art notched rectangle (two 2px steps per corner when n=4)."""
    s = n // 2
    pts = [
        (x, y + n), (x + s, y + n), (x + s, y + s), (x + n, y + s), (x + n, y),
        (x + w - n, y), (x + w - n, y + s), (x + w - s, y + s), (x + w - s, y + n), (x + w, y + n),
        (x + w, y + h - n), (x + w - s, y + h - n), (x + w - s, y + h - s), (x + w - n, y + h - s), (x + w - n, y + h),
        (x + n, y + h), (x + n, y + h - s), (x + s, y + h - s), (x + s, y + h - n), (x, y + h - n),
    ]
    return "M" + "L".join(f"{a} {b}" for a, b in pts) + "z"


def card(x, y, w, h, fill=PANEL, border=BORDER, extra=""):
    """Notched card: 1px outline (outer notch) + panel fill (inset notch)."""
    return (
        f'<path d="{notch_d(x, y, w, h)}" fill="{border}" {extra}/>'
        f'<path d="{notch_d(x + 1, y + 1, w - 2, h - 2)}" fill="{fill}"/>'
    )


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def sprite(rows, palette, x, y, scale):
    """Draw a sprite given as strings; `palette` maps char -> colour ('.' = empty)."""
    by_color = {}
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch != "." and ch in palette:
                start = c
                while c < len(row) and row[c] == ch:
                    c += 1
                by_color.setdefault(palette[ch], []).append(
                    f"M{x + start * scale} {y + r * scale}h{(c - start) * scale}v{scale}h-{(c - start) * scale}z"
                )
            else:
                c += 1
    return "".join(f'<path d="{"".join(p)}" fill="{col}"/>' for col, p in by_color.items())


# --- dithered glow (like the site's bg-glow.png) ------------------------------
_BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dither_glow(w, h, cx, cy, rx, ry, color, opacity, cell=4, strength=1.0):
    parts = []
    for gy in range(h // cell):
        run_start = None
        for gx in range(w // cell + 1):
            px, py = gx * cell + cell / 2, gy * cell + cell / 2
            f = 1 - ((px - cx) / rx) ** 2 - ((py - cy) / ry) ** 2
            on = gx < w // cell and f > 0 and (f * strength) > (_BAYER[gy % 4][gx % 4] + 0.5) / 16
            if on and run_start is None:
                run_start = gx
            elif not on and run_start is not None:
                parts.append(f"M{run_start * cell} {gy * cell}h{(gx - run_start) * cell}v{cell}h-{(gx - run_start) * cell}z")
                run_start = None
    return f'<path d="{"".join(parts)}" fill="{color}" fill-opacity="{opacity}"/>'


def star(x, y, color, cls="", size=2):
    """Little pixel '+' sparkle (matches the 404 starfield)."""
    a = size
    d = f"M{x} {y - a}h{a}v{a}h{a}v{a}h-{a}v{a}h-{a}v-{a}h-{a}v-{a}h{a}z"
    return f'<path d="{d}" fill="{color}" class="{cls}"/>'


def svg(w, h, body, title, desc="", style="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{title}">'
        f"<title>{title}</title>" + (f"<desc>{desc}</desc>" if desc else "")
        + f"<defs>{defs}</defs>"
        + f"<style>{style}"
        + "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        + body + "</svg>"
    )


DOT_GRID = (
    '<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
    f'<rect width="2" height="2" fill="{FG}" fill-opacity=".06"/></pattern>'
)

BLINK_CSS = "@keyframes blink{50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
TWINKLE_CSS = (
    "@keyframes tw{0%,100%{opacity:1}30%{opacity:.3}45%{opacity:.85}70%{opacity:.15}80%{opacity:.6}}"
    ".tw1{animation:tw 3.2s steps(1) infinite}.tw2{animation:tw 3.2s steps(1) -1.1s infinite}"
    ".tw3{animation:tw 3.2s steps(1) -2.2s infinite}"
)
GROW_CSS = (
    "@keyframes grow{from{transform:scaleX(0)}}"
    ".grow{transform-box:fill-box;transform-origin:0 50%;animation:grow 1.1s cubic-bezier(.2,.7,.2,1) both}"
)

SHIELD = (
    ["................", ".hhhhhhhhhhhhhh."]
    + [".h" + "a" * 12 + "h."]
    + [".h" + "aaaa" + "gggg" + "aaaa" + "h."] * 2
    + [".h" + "aaaaa" + "gg" + "aaaaa" + "h."] * 3
    + [".h" + "a" * 12 + "h."]
    + ["..h" + "a" * 10 + "h..", "...h" + "a" * 8 + "h...", "....h" + "a" * 6 + "h....",
       ".....h" + "a" * 4 + "h.....", "......h" + "aa" + "h......", ".......hh......."]
)
SHIELD_PAL = {"h": ACCENT_HI, "a": ACCENT, "g": GOLD}
assert all(len(r) == 16 for r in SHIELD), [len(r) for r in SHIELD]
