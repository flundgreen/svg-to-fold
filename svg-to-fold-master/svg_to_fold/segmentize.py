"""
Extract line segments from an SVG file.

Handles: <line>, <polyline>, <polygon>, <rect>, <path>, <g> (with transforms).
For curved path commands (C, S, Q, T, A) the curve is approximated by a
straight line from start-point to end-point; origami crease patterns virtually
never contain curves, so this is sufficient.

Each returned segment is a 5-tuple:
    (x1, y1, x2, y2, attrs)
where *attrs* is a dict that at minimum contains the key "stroke".

Ported from the behaviour of the npm package svg-segmentize, as used in
src/svg_to_fold.js.
"""

import re
import math
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# SVG namespace helpers
# ---------------------------------------------------------------------------

SVG_NS = "http://www.w3.org/2000/svg"
_NS_RE = re.compile(r"^\{[^}]*\}")


def _local(tag):
    """Strip XML namespace prefix from a tag name."""
    return _NS_RE.sub("", tag)


# ---------------------------------------------------------------------------
# Style / attribute helpers
# ---------------------------------------------------------------------------

def _parse_style(style_str):
    """Parse a CSS inline-style string into a {property: value} dict."""
    result = {}
    for item in style_str.split(";"):
        item = item.strip()
        if ":" in item:
            k, _, v = item.partition(":")
            result[k.strip().lower()] = v.strip()
    return result


def _get_attr(elem, name, default=None):
    """Return element attribute by local name, trying both bare and namespaced."""
    value = elem.get(name)
    if value is None:
        value = elem.get("{%s}%s" % (SVG_NS, name))
    return value if value is not None else default


def _resolve_stroke(elem, inherited):
    """
    Return the effective stroke colour for *elem*.
    Priority: style attribute > stroke attribute > inherited value.
    """
    style_str = _get_attr(elem, "style", "")
    if style_str:
        style = _parse_style(style_str)
        if "stroke" in style:
            s = style["stroke"]
            if s and s.lower() == "none":
                return "none"
            if s and s.lower() not in ("inherit", ""):
                return s
            if s and s.lower() == "inherit":
                return inherited

    stroke = _get_attr(elem, "stroke")
    if stroke and stroke.lower() == "none":
        return "none"
    if stroke and stroke.lower() not in ("none", "inherit", ""):
        return stroke
    if stroke and stroke.lower() == "inherit":
        return inherited

    return inherited


# ---------------------------------------------------------------------------
# 2-D affine transform (represented as [a, b, c, d, e, f] column-major)
#
#  | a  c  e |   | x |
#  | b  d  f | × | y |
#  | 0  0  1 |   | 1 |
# ---------------------------------------------------------------------------

_IDENTITY = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def _compose(parent, child):
    """Return parent ∘ child  (child applied first, then parent)."""
    a1, b1, c1, d1, e1, f1 = parent
    a2, b2, c2, d2, e2, f2 = child
    return [
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    ]


def _apply(matrix, x, y):
    a, b, c, d, e, f = matrix
    return (a * x + c * y + e, b * x + d * y + f)


def _parse_transform(transform_str):
    """
    Parse one SVG transform attribute (may contain multiple functions).
    Returns the composed [a,b,c,d,e,f] matrix.
    """
    result = list(_IDENTITY)
    if not transform_str:
        return result

    for m in re.finditer(r"(\w+)\s*\(([^)]*)\)", transform_str):
        func = m.group(1).lower()
        raw = m.group(2).strip()
        # Split on comma / whitespace, filter empty tokens
        args = [float(t) for t in re.split(r"[,\s]+", raw) if t]

        if func == "matrix" and len(args) >= 6:
            local = args[:6]
        elif func == "translate":
            tx = args[0] if args else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            local = [1.0, 0.0, 0.0, 1.0, tx, ty]
        elif func == "scale":
            sx = args[0] if args else 1.0
            sy = args[1] if len(args) > 1 else sx
            local = [sx, 0.0, 0.0, sy, 0.0, 0.0]
        elif func == "rotate":
            angle = math.radians(args[0]) if args else 0.0
            cx = args[1] if len(args) > 1 else 0.0
            cy = args[2] if len(args) > 2 else 0.0
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            # rotate(angle, cx, cy)
            local = [
                cos_a, sin_a,
                -sin_a, cos_a,
                cx - cx * cos_a + cy * sin_a,
                cy - cx * sin_a - cy * cos_a,
            ]
        elif func == "skewx":
            angle = math.radians(args[0]) if args else 0.0
            local = [1.0, 0.0, math.tan(angle), 1.0, 0.0, 0.0]
        elif func == "skewy":
            angle = math.radians(args[0]) if args else 0.0
            local = [1.0, math.tan(angle), 0.0, 1.0, 0.0, 0.0]
        else:
            continue

        result = _compose(result, local)

    return result


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def _f(s):
    """Parse a float, returning 0.0 on failure."""
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _parse_number_list(s):
    """Split a string into a list of floats (comma/space delimited)."""
    return [float(t) for t in re.split(r"[,\s]+", s.strip()) if t]


# ---------------------------------------------------------------------------
# Per-element segment extraction
# ---------------------------------------------------------------------------

def _seg(x1, y1, x2, y2, matrix, stroke):
    p1 = _apply(matrix, x1, y1)
    p2 = _apply(matrix, x2, y2)
    return (p1[0], p1[1], p2[0], p2[1], {"stroke": stroke})


def _segments_from_line(elem, matrix, stroke):
    x1 = _f(_get_attr(elem, "x1", "0"))
    y1 = _f(_get_attr(elem, "y1", "0"))
    x2 = _f(_get_attr(elem, "x2", "0"))
    y2 = _f(_get_attr(elem, "y2", "0"))
    return [_seg(x1, y1, x2, y2, matrix, stroke)]


def _segments_from_polyline(elem, matrix, stroke, closed=False):
    pts_str = _get_attr(elem, "points", "")
    if not pts_str:
        return []
    nums = _parse_number_list(pts_str)
    if len(nums) < 4:
        return []
    pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
    segs = []
    for i in range(len(pts) - 1):
        segs.append(_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], matrix, stroke))
    if closed and len(pts) >= 3:
        segs.append(_seg(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], matrix, stroke))
    return segs


def _segments_from_rect(elem, matrix, stroke):
    x = _f(_get_attr(elem, "x", "0"))
    y = _f(_get_attr(elem, "y", "0"))
    w = _f(_get_attr(elem, "width", "0"))
    h = _f(_get_attr(elem, "height", "0"))
    if w == 0 or h == 0:
        return []
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    segs = []
    for i in range(4):
        cx1, cy1 = corners[i]
        cx2, cy2 = corners[(i + 1) % 4]
        segs.append(_seg(cx1, cy1, cx2, cy2, matrix, stroke))
    return segs


# ---------------------------------------------------------------------------
# Path 'd' attribute tokeniser and interpreter
# ---------------------------------------------------------------------------

# Matches a command letter or a number token (including negative and scientific)
_PATH_TOKEN = re.compile(
    r"([MmZzLlHhVvCcSsQqTtAa])|"
    r"([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)"
)


def _tokenise_path(d):
    """
    Yield (token_type, value) pairs where token_type is 'cmd' or 'num'.
    """
    for m in _PATH_TOKEN.finditer(d):
        if m.group(1):
            yield ("cmd", m.group(1))
        else:
            yield ("num", float(m.group(2)))


def _iter_path_segments(d):
    """
    Yield raw path segments as (x1, y1, x2, y2) tuples by interpreting the
    path 'd' data attribute.  Curves are approximated as straight lines.
    """
    tokens = list(_tokenise_path(d))
    idx = 0
    n = len(tokens)

    cx, cy = 0.0, 0.0      # current point
    sx, sy = 0.0, 0.0      # sub-path start (for Z)
    cmd = "M"               # current command

    def next_num():
        nonlocal idx
        while idx < n and tokens[idx][0] == "cmd":
            idx += 1
        if idx >= n:
            return None
        val = tokens[idx][1]
        idx += 1
        return val

    def has_num():
        i = idx
        while i < n and tokens[i][0] == "cmd":
            i += 1
        return i < n

    while idx < n:
        tok_type, tok_val = tokens[idx]
        if tok_type == "cmd":
            cmd = tok_val
            idx += 1
        # else: implicit repeat — cmd stays the same, idx not advanced

        c = cmd.upper()

        # ---- MoveTo -------------------------------------------------------
        if c == "M":
            x = next_num(); y = next_num()
            if x is None or y is None:
                break
            if cmd == "m":
                x += cx; y += cy
            cx, cy = x, y
            sx, sy = x, y
            # Implicit LineTo for subsequent coords
            cmd = "l" if cmd == "m" else "L"

        # ---- LineTo -------------------------------------------------------
        elif c == "L":
            x = next_num(); y = next_num()
            if x is None or y is None:
                break
            if cmd == "l":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        # ---- Horizontal LineTo -------------------------------------------
        elif c == "H":
            x = next_num()
            if x is None:
                break
            if cmd == "h":
                x += cx
            yield (cx, cy, x, cy)
            cx = x

        # ---- Vertical LineTo ---------------------------------------------
        elif c == "V":
            y = next_num()
            if y is None:
                break
            if cmd == "v":
                y += cy
            yield (cx, cy, cx, y)
            cy = y

        # ---- ClosePath ---------------------------------------------------
        elif c == "Z":
            if (cx, cy) != (sx, sy):
                yield (cx, cy, sx, sy)
            cx, cy = sx, sy

        # ---- Cubic Bézier (approximate) ----------------------------------
        elif c == "C":
            x1 = next_num(); y1 = next_num()
            x2 = next_num(); y2 = next_num()
            x  = next_num(); y  = next_num()
            if x is None:
                break
            if cmd == "c":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        # ---- Smooth Cubic Bézier (approximate) ---------------------------
        elif c == "S":
            x2 = next_num(); y2 = next_num()
            x  = next_num(); y  = next_num()
            if x is None:
                break
            if cmd == "s":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        # ---- Quadratic Bézier (approximate) ------------------------------
        elif c == "Q":
            x1 = next_num(); y1 = next_num()
            x  = next_num(); y  = next_num()
            if x is None:
                break
            if cmd == "q":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        # ---- Smooth Quadratic Bézier (approximate) -----------------------
        elif c == "T":
            x = next_num(); y = next_num()
            if x is None:
                break
            if cmd == "t":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        # ---- Elliptical Arc (approximate as straight line) ---------------
        elif c == "A":
            _rx = next_num(); _ry = next_num()
            _rot = next_num(); _large = next_num(); _sweep = next_num()
            x = next_num(); y = next_num()
            if x is None:
                break
            if cmd == "a":
                x += cx; y += cy
            yield (cx, cy, x, y)
            cx, cy = x, y

        else:
            # Unknown command — skip one token to avoid infinite loop
            idx += 1


def _segments_from_path(elem, matrix, stroke):
    d = _get_attr(elem, "d", "")
    if not d:
        return []
    segs = []
    for x1, y1, x2, y2 in _iter_path_segments(d):
        segs.append(_seg(x1, y1, x2, y2, matrix, stroke))
    return segs


# ---------------------------------------------------------------------------
# Recursive element walker
# ---------------------------------------------------------------------------

_SHAPE_HANDLERS = {
    "line":     _segments_from_line,
    "polyline": lambda e, m, s: _segments_from_polyline(e, m, s, closed=False),
    "polygon":  lambda e, m, s: _segments_from_polyline(e, m, s, closed=True),
    "rect":     _segments_from_rect,
    "path":     _segments_from_path,
}

# Tags that should be traversed (group-like)
_CONTAINER_TAGS = {"g", "svg", "symbol", "defs", "a", "marker", "mask", "clippath"}


def _walk(elem, parent_matrix, inherited_stroke, segments):
    tag = _local(elem.tag)

    # Accumulate local transform
    local_tf = _parse_transform(_get_attr(elem, "transform", ""))
    matrix = _compose(parent_matrix, local_tf)

    # Resolve stroke (inheriting from parent)
    stroke = _resolve_stroke(elem, inherited_stroke)

    if tag in _SHAPE_HANDLERS:
        segments.extend(_SHAPE_HANDLERS[tag](elem, matrix, stroke))

    # Always recurse — some shapes (like <g>) wrap other shapes
    if tag in _CONTAINER_TAGS or tag == "svg":
        for child in elem:
            _walk(child, matrix, stroke, segments)
    elif tag not in _SHAPE_HANDLERS:
        # Unknown element — try to recurse anyway (e.g. namespaced groups)
        for child in elem:
            _walk(child, matrix, stroke, segments)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def segmentize(svg_input):
    """
    Parse *svg_input* (a file path, file-like object, or XML string) and
    return a list of 5-tuples  (x1, y1, x2, y2, {"stroke": colour_string}).

    Zero-length segments are filtered out.
    """
    # Parse SVG
    if isinstance(svg_input, str) and not svg_input.lstrip().startswith("<"):
        # Treat as file path
        tree = ET.parse(svg_input)
        root = tree.getroot()
    elif hasattr(svg_input, "read"):
        tree = ET.parse(svg_input)
        root = tree.getroot()
    else:
        # XML string
        root = ET.fromstring(svg_input)

    segments = []
    _walk(root, list(_IDENTITY), "black", segments)

    # Filter zero-length segments and segments with no stroke
    eps = 1e-9
    segments = [
        s for s in segments
        if (abs(s[2] - s[0]) > eps or abs(s[3] - s[1]) > eps)
        and s[4].get("stroke", "").lower() != "none"
    ]
    return segments
