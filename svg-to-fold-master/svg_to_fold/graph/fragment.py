"""
Fragment: split overlapping edges at intersection points and rebuild the
planar graph so that every edge-crossing becomes a shared vertex.

Ported from src/graph/fragment.js
"""

import math as _math

from .math_utils import EPSILON, equivalent, edge_edge_exclusive, point_on_edge_exclusive
from .remove import remove_geometry_key_indices


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _edges_vertices_equivalent(a, b):
    """True if two edge vertex-pairs represent the same undirected edge."""
    return (a[0] == b[0] and a[1] == b[1]) or (a[0] == b[1] and a[1] == b[0])


def _make_edges_alignment(graph):
    """
    For each edge, return True if it is more horizontal than vertical
    (|dx| > |dy|, i.e. |cos(angle)| > 0.707).
    Used to choose whether to sort split-points by x or by y.
    """
    coords = graph["vertices_coords"]
    alignments = []
    for v1, v2 in graph["edges_vertices"]:
        dx = coords[v2][0] - coords[v1][0]
        dy = coords[v2][1] - coords[v1][1]
        length = _math.sqrt(dx * dx + dy * dy)
        if length == 0:
            alignments.append(True)
        else:
            alignments.append(abs(dx / length) > 0.707)
    return alignments


def _make_edges_intersections(graph, epsilon=EPSILON):
    """
    Find all pairwise interior intersection points between edges.
    Returns a list-of-lists: edges_intersections[i] is a list of [x,y]
    points where edge i crosses other edges.
    """
    coords = graph["vertices_coords"]
    edges = [[coords[v1], coords[v2]] for v1, v2 in graph["edges_vertices"]]
    n = len(edges)
    edges_intersections = [[] for _ in range(n)]

    for i in range(n - 1):
        for j in range(i + 1, n):
            pt = edge_edge_exclusive(
                edges[i][0], edges[i][1],
                edges[j][0], edges[j][1],
                epsilon
            )
            if pt is not None:
                edges_intersections[i].append(pt)
                edges_intersections[j].append(pt)

    return edges_intersections


def _make_edges_collinear_vertices(graph, epsilon=EPSILON):
    """
    For each edge, find all vertices (from vertices_coords) that lie on
    the edge — including the edge's own endpoints.
    Returns a list-of-lists of coordinate arrays [x, y].
    """
    coords = graph["vertices_coords"]
    edges = [[coords[v1], coords[v2]] for v1, v2 in graph["edges_vertices"]]
    result = []
    for e0, e1 in edges:
        on_edge = [v for v in coords if point_on_edge_exclusive(v, e0, e1, epsilon)]
        result.append(on_edge)
    return result


# ---------------------------------------------------------------------------
# Main fragment function
# ---------------------------------------------------------------------------

def fragment(graph, epsilon=EPSILON):
    """
    Split all edges at their mutual intersection points (and at any existing
    vertices lying on them), then deduplicate vertices and edges.

    Preserves edges_assignment and edges_foldAngle from the original edges.
    Returns a new graph dict with only:
      vertices_coords, edges_vertices, edges_assignment, edges_foldAngle
    (face data is discarded — recompute afterwards).
    """
    horiz_sort = lambda pt: pt[0]
    vert_sort  = lambda pt: pt[1]

    edges_alignment = _make_edges_alignment(graph)
    edges_intersections = _make_edges_intersections(graph, epsilon)
    edges_collinear = _make_edges_collinear_vertices(graph, epsilon)

    # Combine intersection points + collinear vertices for each edge,
    # then sort along the dominant axis so consecutive pairs form sub-edges.
    combined = [
        edges_intersections[i] + edges_collinear[i]
        for i in range(len(graph["edges_vertices"]))
    ]
    for i, pts in enumerate(combined):
        key = horiz_sort if edges_alignment[i] else vert_sort
        pts.sort(key=key)

    # Build sub-edges as consecutive coordinate pairs
    new_edges_by_orig = [
        [[pts[k], pts[k + 1]] for k in range(len(pts) - 1)]
        for pts in combined
    ]

    # Remove degenerate (zero-length) sub-edges
    def is_degenerate(sub_edge):
        return all(
            abs(sub_edge[0][dim] - sub_edge[1][dim]) < epsilon
            for dim in range(2)
        )
    new_edges_by_orig = [
        [se for se in group if not is_degenerate(se)]
        for group in new_edges_by_orig
    ]

    # edge_map[j] = original edge index that produced sub-edge j
    edge_map = []
    for orig_i, group in enumerate(new_edges_by_orig):
        edge_map.extend([orig_i] * len(group))

    # Flatten all sub-edge coordinates into a new vertices_coords list,
    # and assign sequential vertex indices.
    new_vertices_coords = []
    new_edges_vertices = []
    counter = 0
    for group in new_edges_by_orig:
        for se in group:
            new_vertices_coords.append(se[0])
            new_vertices_coords.append(se[1])
            new_edges_vertices.append([counter, counter + 1])
            counter += 2

    # --- Deduplicate vertices ---
    n_verts = len(new_vertices_coords)
    # vertices_equivalent[i][j] = True if vertex i and j are within epsilon
    vertices_equivalent = [[False] * n_verts for _ in range(n_verts)]
    for i in range(n_verts - 1):
        for j in range(i + 1, n_verts):
            vertices_equivalent[i][j] = equivalent(
                new_vertices_coords[i], new_vertices_coords[j], epsilon
            )

    # vertices_map[i] = canonical index for vertex i
    vertices_map = [None] * n_verts
    for i in range(n_verts - 1):
        for j in range(i + 1, n_verts):
            if vertices_equivalent[i][j]:
                vertices_map[j] = i if vertices_map[i] is None else vertices_map[i]

    vertices_remove = [m is not None for m in vertices_map]
    for i in range(n_verts):
        if vertices_map[i] is None:
            vertices_map[i] = i

    # Remap edge vertex indices
    for ev in new_edges_vertices:
        ev[0] = vertices_map[ev[0]]
        ev[1] = vertices_map[ev[1]]

    # --- Deduplicate edges ---
    n_edges = len(new_edges_vertices)
    edges_equivalent = [[False] * n_edges for _ in range(n_edges)]
    for i in range(n_edges - 1):
        for j in range(i + 1, n_edges):
            edges_equivalent[i][j] = _edges_vertices_equivalent(
                new_edges_vertices[i], new_edges_vertices[j]
            )

    # Save the *last* occurrence of each duplicate group (matches JS behaviour)
    edges_map = [None] * n_edges
    for i in range(n_edges - 1):
        for j in range(i + 1, n_edges):
            if edges_equivalent[i][j]:
                edges_map[i] = j if edges_map[j] is None else edges_map[j]

    edges_dont_remove = [m is None for m in edges_map]
    for i in range(n_edges):
        if edges_map[i] is None:
            edges_map[i] = i

    edges_vertices_cl = [ev for i, ev in enumerate(new_edges_vertices) if edges_dont_remove[i]]
    edge_map_cl = [edge_map[i] for i in range(n_edges) if edges_dont_remove[i]]

    flat = {
        "vertices_coords": new_vertices_coords,
        "edges_vertices": edges_vertices_cl,
    }
    # Only copy per-edge arrays when they are populated to the correct length.
    # (In JS, out-of-bounds array access returns undefined; Python raises.)
    n_orig_edges = len(graph["edges_vertices"])
    ea = graph.get("edges_assignment", [])
    if ea and len(ea) >= n_orig_edges:
        flat["edges_assignment"] = [ea[i] for i in edge_map_cl]
    efa = graph.get("edges_foldAngle", [])
    if efa and len(efa) >= n_orig_edges:
        flat["edges_foldAngle"] = [efa[i] for i in edge_map_cl]

    # Remove duplicate vertices (those that were remapped to another)
    vertices_remove_indices = [i for i, rm in enumerate(vertices_remove) if rm]
    remove_geometry_key_indices(flat, "vertices", vertices_remove_indices)

    return flat
