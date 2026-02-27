"""
Main SVG → FOLD conversion pipeline.

Ported from src/svg_to_fold.js.

Pipeline:
  1. Segmentize SVG → raw line segments with colour attributes.
  2. Build initial FOLD graph: vertices from segment endpoints, edges from
     segments, edge assignments from stroke colours.
  3. Fragment: split every pair of crossing edges at their intersection,
     deduplicate vertices and edges.
  3a. Remove artifact edges (too short relative to bounding-box diagonal).
  4. Compute face topology (vertices_vertices → faces_vertices → faces_edges).
  5. Optionally mark boundary edges as "B".
  6. Compute derived arrays (edges_length, vertices_faces, edges_faces).
"""

import math

from .segmentize import segmentize
from .color import color_to_assignment
from .graph.fragment import fragment
from .graph.remove import remove_geometry_key_indices
from .graph.faces import (
    edges_vertices_to_vertices_vertices_sorted,
    vertices_vertices_to_faces_vertices,
    faces_vertices_to_faces_edges,
    compute_vertices_faces,
    compute_edges_faces,
    compute_edges_length,
)
from .graph.boundary import find_boundary

# FOLD assignment → dihedral fold angle (degrees)
_ASSIGNMENT_TO_FOLD_ANGLE = {
    "V": 180, "v": 180,
    "M": -180, "m": -180,
}


def _remove_short_edges(graph, min_length):
    """
    Remove edges shorter than *min_length* (in SVG user units) and any
    vertices that become isolated as a result.
    """
    coords = graph["vertices_coords"]
    short = []
    for i, (v1, v2) in enumerate(graph["edges_vertices"]):
        p1, p2 = coords[v1], coords[v2]
        d = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        if d < min_length:
            short.append(i)
    if not short:
        return
    remove_geometry_key_indices(graph, "edges", short)
    used = set(v for ev in graph["edges_vertices"] for v in ev)
    isolate = [i for i in range(len(graph["vertices_coords"])) if i not in used]
    if isolate:
        remove_geometry_key_indices(graph, "vertices", isolate)


def _merge_nearby_vertices(graph, tolerance):
    """
    Merge any two vertices that are within *tolerance* SVG user units of each
    other.  After merging, duplicate edges and isolated vertices are removed.
    """
    if tolerance <= 0:
        return
    coords = graph["vertices_coords"]
    n = len(coords)
    # Build a canonical-index map: vertices_map[i] = representative index
    vertices_map = list(range(n))

    def root(i):
        while vertices_map[i] != i:
            vertices_map[i] = vertices_map[vertices_map[i]]
            i = vertices_map[i]
        return i

    for i in range(n - 1):
        for j in range(i + 1, n):
            ri, rj = root(i), root(j)
            if ri == rj:
                continue
            dx = coords[ri][0] - coords[rj][0]
            dy = coords[ri][1] - coords[rj][1]
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                vertices_map[rj] = ri  # merge j into i

    # Build a compact remapping
    canonical = [root(i) for i in range(n)]
    unique = sorted(set(canonical))
    old_to_new = {old: new for new, old in enumerate(unique)}

    # Check if anything actually merged
    if len(unique) == n:
        return

    graph["vertices_coords"] = [coords[u] for u in unique]
    graph["edges_vertices"] = [
        [old_to_new[canonical[v1]], old_to_new[canonical[v2]]]
        for v1, v2 in graph["edges_vertices"]
    ]

    # Remove self-loop edges (merged endpoints)
    keep = [i for i, (v1, v2) in enumerate(graph["edges_vertices"]) if v1 != v2]
    remove_geometry_key_indices(graph, "edges", [i for i in range(len(graph["edges_vertices"])) if i not in set(keep)])

    # Remove duplicate edges (keep last occurrence, matching fragment behaviour)
    seen = {}
    dups = []
    for i, (v1, v2) in enumerate(graph["edges_vertices"]):
        key = (min(v1, v2), max(v1, v2))
        if key in seen:
            dups.append(seen[key])
        seen[key] = i
    if dups:
        remove_geometry_key_indices(graph, "edges", sorted(set(dups)))


def _split_edges_at_pendant_vertices(graph, tolerance):
    """
    For each degree-1 (pendant) vertex, find any edge the pendant lies on
    (within *tolerance* px, using the triangle-inequality test) and split
    that edge into two sub-edges at the pendant vertex.

    This fixes the case where a spoke endpoint was merged near a boundary
    edge due to SVG integer rounding: after vertex merging the pendant
    may sit within merge_tolerance px of the edge but outside the
    deduplication epsilon, so the fragment step didn't create a shared
    vertex and the face cannot be traced.
    """
    coords = graph["vertices_coords"]
    ev = graph["edges_vertices"]
    ea = graph.get("edges_assignment", [])
    has_ea = len(ea) == len(ev)

    # Compute degree of every vertex
    degree = [0] * len(coords)
    for v1, v2 in ev:
        degree[v1] += 1
        degree[v2] += 1

    pendants = [i for i, d in enumerate(degree) if d == 1]
    if not pendants:
        return

    # For each pendant vertex, find edges it lies on (but is not an endpoint of)
    splits_by_edge = {}
    for pv in pendants:
        px, py = coords[pv]
        for ei, (v1, v2) in enumerate(ev):
            if v1 == pv or v2 == pv:
                continue
            e0x, e0y = coords[v1]
            e1x, e1y = coords[v2]
            d_edge = math.sqrt((e0x - e1x) ** 2 + (e0y - e1y) ** 2)
            d_p0   = math.sqrt((e0x - px)  ** 2 + (e0y - py)  ** 2)
            d_p1   = math.sqrt((e1x - px)  ** 2 + (e1y - py)  ** 2)
            if abs(d_edge - d_p0 - d_p1) <= tolerance:
                splits_by_edge.setdefault(ei, []).append(pv)

    if not splits_by_edge:
        return

    new_ev = list(ev)
    new_ea = list(ea) if has_ea else None

    # Process in reverse index order so earlier indices remain valid
    for ei in sorted(splits_by_edge.keys(), reverse=True):
        split_verts = splits_by_edge[ei]
        v1, v2 = new_ev[ei]
        e0x, e0y = coords[v1]

        # Sort split vertices by distance from v1
        split_verts_sorted = sorted(
            split_verts,
            key=lambda pv: (coords[pv][0] - e0x) ** 2 + (coords[pv][1] - e0y) ** 2
        )

        chain = [v1] + split_verts_sorted + [v2]
        sub = [[chain[k], chain[k + 1]] for k in range(len(chain) - 1)]

        new_ev[ei:ei + 1] = sub
        if new_ea is not None:
            orig = new_ea[ei]
            new_ea[ei:ei + 1] = [orig] * len(sub)

    graph["edges_vertices"] = new_ev
    if new_ea is not None:
        graph["edges_assignment"] = new_ea


def _fix_degenerate_faces(graph):
    """
    Split faces that contain a repeated vertex into valid sub-faces.

    A degenerate face such as [A, X, Y, A, Z] arises when the half-edge walk
    bounces back through a pendant (degree-1) vertex like a petal-tip spoke.
    We split at the first repeated vertex and keep only parts that have ≥ 3
    vertices and positive signed area (interior faces in SVG Y-down coords).
    """
    def _signed_area(coords, verts):
        area = 0.0
        n = len(verts)
        for i in range(n):
            x1, y1 = coords[verts[i]]
            x2, y2 = coords[verts[(i + 1) % n]]
            area += x1 * y2 - x2 * y1
        return area / 2.0

    coords = graph["vertices_coords"]
    fixed = []
    for fv in graph.get("faces_vertices", []):
        if len(fv) == len(set(fv)):
            fixed.append(fv)
            continue
        # Find first repeated vertex
        seen = {}
        split_i = None
        for i, v in enumerate(fv):
            if v in seen:
                split_i = (seen[v], i)
                break
            seen[v] = i
        if split_i is None:
            fixed.append(fv)
            continue
        j, i = split_i   # fv[j] == fv[i], j < i
        part1 = fv[:i]   # e.g. [A, X, Y]  for j=0, i=3
        part2 = fv[i:]   # e.g. [A, Z]     for i=3
        for part in (part1, part2):
            if len(part) >= 3 and _signed_area(coords, part) > 0:
                fixed.append(part)
    graph["faces_vertices"] = fixed


def _empty_fold():
    return {
        "file_spec": 1.1,
        "file_creator": "svg-to-fold (Python)",
        "file_classes": ["singleModel"],
        "frame_title": "",
        "frame_classes": ["creasePattern"],
        "frame_attributes": ["2D"],
        "vertices_coords": [],
        "vertices_vertices": [],
        "vertices_faces": [],
        "edges_vertices": [],
        "edges_faces": [],
        "edges_assignment": [],
        "edges_foldAngle": [],
        "edges_length": [],
        "faces_vertices": [],
        "faces_edges": [],
    }


def svg_to_fold(svg_input, epsilon=None, boundary=True, merge_tolerance=1.0):
    """
    Convert an SVG file (path, file-like object, or XML string) to a FOLD
    graph dict.

    Parameters
    ----------
    svg_input : str | file-like
        Path to an SVG file, an open file object, or an XML string.
    epsilon : float | None
        Floating-point tolerance for vertex deduplication and intersection
        tests.  Defaults to 1e-6 when None.
    boundary : bool
        When True (default), detect the outer boundary and mark those edges
        with assignment "B".
    merge_tolerance : float
        Vertices within this many SVG user-unit pixels of each other are
        merged into one.  Keeps the graph clean when the SVG editor rounds
        coordinates to integers.  Default is 1.0.  Set to 0 to disable.

    Returns
    -------
    dict
        A FOLD-format dict ready for JSON serialisation.
    """
    from .graph.math_utils import EPSILON as _DEFAULT_EPS
    if epsilon is None:
        epsilon = _DEFAULT_EPS

    # ------------------------------------------------------------------ #
    # 1. Extract line segments from the SVG
    # ------------------------------------------------------------------ #
    segments = segmentize(svg_input)

    # ------------------------------------------------------------------ #
    # 2. Build pre-fragment FOLD graph
    # ------------------------------------------------------------------ #
    pre = _empty_fold()
    v0 = 0  # starting vertex index (always 0 for a fresh graph)

    for i, seg in enumerate(segments):
        x1, y1, x2, y2 = seg[0], seg[1], seg[2], seg[3]
        pre["vertices_coords"].append([x1, y1])
        pre["vertices_coords"].append([x2, y2])
        pre["edges_vertices"].append([v0 + i * 2, v0 + i * 2 + 1])

        attrs = seg[4] if len(seg) > 4 else None
        stroke = attrs.get("stroke") if attrs else None
        pre["edges_assignment"].append(color_to_assignment(stroke))

    if not pre["edges_vertices"]:
        return pre  # empty SVG

    # ------------------------------------------------------------------ #
    # 3. Fragment (split crossing edges, deduplicate vertices/edges)
    # ------------------------------------------------------------------ #
    graph = fragment(pre, epsilon)

    # ------------------------------------------------------------------ #
    # 3a. Merge nearby vertices (SVG rounding artefacts)
    # ------------------------------------------------------------------ #
    _merge_nearby_vertices(graph, merge_tolerance)

    # ------------------------------------------------------------------ #
    # 3b. Remove edges too short to be real crease lines (SVG artefacts).
    #     Threshold: 1 % of the bounding-box diagonal.
    # ------------------------------------------------------------------ #
    coords = graph["vertices_coords"]
    if len(coords) >= 2:
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        diag = math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2)
        _remove_short_edges(graph, diag * 0.01)

    # ------------------------------------------------------------------ #
    # 3c. Split edges at pendant (degree-1) vertices that lie on them.
    #     Needed when SVG rounding leaves a spoke endpoint within
    #     merge_tolerance px of a boundary edge without touching it.
    # ------------------------------------------------------------------ #
    _split_edges_at_pendant_vertices(graph, merge_tolerance)

    # ------------------------------------------------------------------ #
    # 4. Compute face topology
    # ------------------------------------------------------------------ #
    edges_vertices_to_vertices_vertices_sorted(graph)
    vertices_vertices_to_faces_vertices(graph)
    _fix_degenerate_faces(graph)
    faces_vertices_to_faces_edges(graph)

    # ------------------------------------------------------------------ #
    # 5. Fold angles
    # ------------------------------------------------------------------ #
    graph["edges_foldAngle"] = [
        _ASSIGNMENT_TO_FOLD_ANGLE.get(a, 0)
        for a in graph.get("edges_assignment", [])
    ]

    # ------------------------------------------------------------------ #
    # 6. Boundary detection
    # ------------------------------------------------------------------ #
    if boundary:
        for edge_idx in find_boundary(graph):
            graph["edges_assignment"][edge_idx] = "B"
            graph["edges_foldAngle"][edge_idx] = None

        # Post-filter: remove faces whose every edge is a boundary edge.
        # These are outer-boundary-polygon faces (e.g. a decorative border
        # rectangle disconnected from the crease pattern).  Real crease-
        # pattern faces always have at least one non-boundary edge.
        b_edges = {i for i, a in enumerate(graph["edges_assignment"]) if a == "B"}
        keep = [
            i for i, fe in enumerate(graph["faces_edges"])
            if not all(e in b_edges for e in fe)
        ]
        graph["faces_vertices"] = [graph["faces_vertices"][i] for i in keep]
        graph["faces_edges"] = [graph["faces_edges"][i] for i in keep]

    # ------------------------------------------------------------------ #
    # 7. Derived arrays
    # ------------------------------------------------------------------ #
    compute_edges_length(graph)
    compute_vertices_faces(graph)
    compute_edges_faces(graph)

    # Ensure the output contains all canonical FOLD keys
    for key in ("vertices_vertices", "vertices_faces",
                "edges_faces", "edges_length"):
        if key not in graph:
            graph[key] = []

    return graph
