"""
Geometric math primitives — ported from src/graph/math.js
"""

import math

EPSILON = 1e-6


def magnitude(v):
    return math.sqrt(sum(c * c for c in v))


def normalize(v):
    m = magnitude(v)
    return v if m == 0 else [c / m for c in v]


def equivalent(a, b, epsilon=EPSILON):
    """Return True if two coordinate arrays are within epsilon of each other."""
    return all(abs(a[i] - b[i]) <= epsilon for i in range(len(a)))


def _det(a, b):
    return a[0] * b[1] - b[0] * a[1]


def edge_edge_exclusive(a0, a1, b0, b1, epsilon=EPSILON):
    """
    Find the intersection point of two line segments, exclusive of endpoints.
    Returns [x, y] if the segments cross strictly in their interiors, else None.
    Matches edge_edge_exclusive in math.js.
    """
    aVec = [a1[0] - a0[0], a1[1] - a0[1]]
    bVec = [b1[0] - b0[0], b1[1] - b0[1]]

    denominator0 = _det(aVec, bVec)
    if abs(denominator0) < epsilon:
        return None  # parallel

    denominator1 = -denominator0
    diff_ab = [b0[0] - a0[0], b0[1] - a0[1]]
    diff_ba = [a0[0] - b0[0], a0[1] - b0[1]]
    numerator0 = _det(diff_ab, bVec)
    numerator1 = _det(diff_ba, aVec)

    t0 = numerator0 / denominator0
    t1 = numerator1 / denominator1

    if t0 > EPSILON and t0 < 1 - EPSILON and t1 > EPSILON and t1 < 1 - EPSILON:
        return [a0[0] + aVec[0] * t0, a0[1] + aVec[1] * t0]
    return None


def point_on_edge_exclusive(point, edge0, edge1, epsilon=EPSILON):
    """
    Return True if *point* lies on the segment [edge0, edge1].
    Uses triangle-inequality equality check (inclusive of endpoints).
    Matches point_on_edge_exclusive in math.js.
    """
    d_edge = math.sqrt((edge0[0] - edge1[0]) ** 2 + (edge0[1] - edge1[1]) ** 2)
    d_p0 = math.sqrt((edge0[0] - point[0]) ** 2 + (edge0[1] - point[1]) ** 2)
    d_p1 = math.sqrt((edge1[0] - point[0]) ** 2 + (edge1[1] - point[1]) ** 2)
    return abs(d_edge - d_p0 - d_p1) < epsilon
