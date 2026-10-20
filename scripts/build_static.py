#!/usr/bin/env python3
"""Build the static pixel-art graphics in ./assets (header, section headings, cert badges).

Run from the repo root:  python scripts/build_static.py
Edit the DATA section below when your certs change, then re-run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)
W = 830


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote assets/" + name, f"({len(content) / 1024:.1f} KB)")


def clip_for(w, h, cid="clip"):
    return f'<clipPath id="{cid}"><path d="{notch_d(0, 0, w, h)}"/></clipPath>'


# =============================================================================
# DATA (from bransonbailey.github.io)
# =============================================================================
CERTS = [  # name, issuer, note
    ("CSAP", "COMPTIA", "THRU 2029"),
    ("CYSA+", "COMPTIA", "THRU 2029"),
    ("SECURITY+", "COMPTIA", "THRU 2029"),
    ("AWS CCP", "AWS", "THRU 2028"),
    ("IBM EDTP", "IBM", "SINCE 2024"),
]


# =============================================================================
# header.svg
# =============================================================================
def header():
    h = 210
    stars = (
        star(612, 30, GOLD, "tw1") + star(760, 62, FG, "tw2", 1) + star(700, 150, GOLD, "tw3")
        + star(120, 24, FG, "tw3", 1) + star(560, 176, FG, "tw1", 1) + star(792, 120, ACCENT_HI, "tw2", 1)
        + star(40, 170, GOLD, "tw2")
    )
    name_x, name_y = 192, 62
    name = "BRANSON BAILEY"
    cur_x = name_x + len(name) * 36
    body = (
        card(0, 0, W, h, fill=BG)
        + '<g clip-path="url(#clip)">'
        + f'<rect width="{W}" height="{h}" fill="url(#dots)"/>'
        + dither_glow(W, h, 330, 105, 430, 120, ACCENT, 0.22)
        + stars
        + "</g>"
        # shield mark
        + f'<g filter="url(#glow)" opacity=".55">{sprite(SHIELD, SHIELD_PAL, 48, 48, 8)}</g>'
        + sprite(SHIELD, SHIELD_PAL, 48, 48, 8)
        # title with soft glow, like the site's h1 text-shadow
        + f'<g filter="url(#glow)" opacity=".6">{text(name, name_x, name_y, 6, ACCENT)}</g>'
        + text(name, name_x, name_y, 6, ACCENT)
        + text("_", cur_x, name_y, 6, GOLD, extra='class="blink"')
        + text("BRANSONBAILEY.GITHUB.IO", name_x + 2, name_y + 66, 3, ACCENT_HI)
        + text("BB//", 24, 20, 2, ACCENT)
    )
    defs = (
        DOT_GRID + clip_for(W, h)
        + '<filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>'
    )
    return svg(W, h, body, "Branson Bailey - Cybersecurity",
               "Pixel-art banner: Branson Bailey, cybersecurity student, IT security intern and penetration tester.",
               style=BLINK_CSS + TWINKLE_CSS, defs=defs)


# =============================================================================
# section headings
# =============================================================================
def heading(label, idx):
    h = 40
    lw = text_width(label, 3)
    body = (
        card(0, 0, W, h, fill=BG)
        + text(">", 18, 9, 3, GOLD)
        + text(label, 44, 9, 3, ACCENT_HI)
        + text("_", 44 + lw + 6, 9, 3, GOLD, extra='class="blink"')
        + text(idx, 812, 13, 2, FAINT, anchor="end")
    )
    return svg(W, h, body, label.title(), style=BLINK_CSS)


# =============================================================================
# certs
# =============================================================================
CHECK = ["......gg", ".....gg.", "gg..gg..", ".gggg...", "..gg...."]


def certs():
    gap, h = 10, 106
    cw = (W - gap * 4) // 5
    body = ""
    for i, (name, issuer, note) in enumerate(CERTS):
        x = i * (cw + gap)
        sc = 3 if text_width(name, 3) <= cw - 58 else 2
        ny = 20 if sc == 3 else 24
        body += card(x, 0, cw, h)
        body += sprite(CHECK, {"g": GOLD}, x + cw - 30, 12, 2)
        body += text(name, x + 14, ny, sc, ACCENT_HI)
        body += text(issuer, x + 14, 58, 2, FG)
        body += text(note, x + 14, 80, 2, MUTED)
    return svg(W, h, body, "Certifications",
               "CompTIA CSAP, CySA+, Security+, AWS Certified Cloud Practitioner, IBM Enterprise Design Thinking Practitioner.")


if __name__ == "__main__":
    save("header.svg", header())
    for name, label, idx in [
        ("h-about.svg", "ABOUT", "01"),
        ("h-certs.svg", "CERTIFICATIONS", "02"), ("h-activity.svg", "ACTIVITY", "03"),
    ]:
        save(name, heading(label, idx))
    save("certs.svg", certs())
