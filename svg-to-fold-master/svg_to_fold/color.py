"""
Map SVG stroke colour strings to FOLD edge-assignment codes.

  Red-dominant  →  "M"  (mountain fold)
  Blue-dominant →  "V"  (valley fold)
  Otherwise     →  "U"  (unassigned)

Ported from src/color_to_assignment.js
"""

from .css_colors import CSS_COLORS


def _hex_to_components(h):
    """
    Parse a CSS hex colour (#RGB, #RRGGBB, #RGBA, #RRGGBBAA) into
    normalised [r, g, b, a] floats in the range [0, 1].
    """
    h = h.strip()
    if not h.startswith("#"):
        return [0.0, 0.0, 0.0, 1.0]

    body = h[1:]
    length = len(body)

    if length == 3:
        r = int(body[0] * 2, 16)
        g = int(body[1] * 2, 16)
        b = int(body[2] * 2, 16)
        a = 255
    elif length == 6:
        r = int(body[0:2], 16)
        g = int(body[2:4], 16)
        b = int(body[4:6], 16)
        a = 255
    elif length == 4:
        r = int(body[0] * 2, 16)
        g = int(body[1] * 2, 16)
        b = int(body[2] * 2, 16)
        a = int(body[3] * 2, 16)
    elif length == 8:
        r = int(body[0:2], 16)
        g = int(body[2:4], 16)
        b = int(body[4:6], 16)
        a = int(body[6:8], 16)
    else:
        return [0.0, 0.0, 0.0, 1.0]

    return [r / 255.0, g / 255.0, b / 255.0, a / 255.0]


def color_to_assignment(color_string):
    """
    Convert a CSS colour string to a FOLD edge-assignment letter.

    Returns one of:  "M" (mountain), "V" (valley), "U" (unassigned).
    """
    if not color_string or not isinstance(color_string, str):
        return "U"

    color_string = color_string.strip().lower()

    # Resolve named colours
    c = [0.0, 0.0, 0.0, 1.0]
    if color_string.startswith("#"):
        c = _hex_to_components(color_string)
    elif color_string in CSS_COLORS:
        c = _hex_to_components(CSS_COLORS[color_string])
    # "none", "inherit", unknown → default black → "U"

    ep = 0.05
    r, g, b = c[0], c[1], c[2]

    # Near-black → unassigned
    if r < ep and g < ep and b < ep:
        return "U"

    # Red-dominant → mountain
    if r > g and (r - b) > ep:
        return "M"

    # Blue-dominant → valley
    if b > g and (b - r) > ep:
        return "V"

    return "U"
