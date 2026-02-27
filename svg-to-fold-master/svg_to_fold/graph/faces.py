"""
Compute planar-graph face topology from edges.

Ports the three FOLD library conversion functions used in svg_to_fold.js:
  FOLD.convert.edges_vertices_to_vertices_vertices_sorted
  FOLD.convert.vertices_vertices_to_faces_vertices
  FOLD.convert.faces_vertices_to_faces_edges

Algorithm overview
------------------
1. Build an adjacency list for every vertex, sorted by angle (CCW in
   standard math coords; in SVG Y-is-down coords atan2 gives a consistent
   ordering that produces correct planar faces).

2. Trace faces using a half-edge traversal:
   For half-edge (u → v), the *next* half-edge in the same face is
   (v → w) where w = vertices_vertices[v][(indexOf(u) + 1) % degree(v)].
   This is the same convention used in boundary.js.

3. Discard the outer (infinite) face, identified by negative signed area
   in SVG (Y-down) coordinates (the shoelace formula gives a negative
   result for the CCW-wound outer boundary).
"""

import math


def edges_vertices_to_vertices_vertices_sorted(graph):
    """
    Populate graph['vertices_vertices'] with per-vertex neighbour lists
    sorted by polar angle (atan2) around each vertex.
    Modifies graph in-place.
    """
    coords = graph["vertices_coords"]
    n = len(coords)
    vv = [[] for _ in range(n)]

    for v1, v2 in graph["edges_vertices"]:
        vv[v1].append(v2)
        vv[v2].append(v1)

    for v, neighbors in enumerate(vv):
        cx, cy = coords[v]
        neighbors.sort(key=lambda nb: math.atan2(
            coords[nb][1] - cy,
            coords[nb][0] - cx
        ))

    graph["vertices_vertices"] = vv


def _signed_area(coords, face_verts):
    """Shoelace signed area. Positive ↔ CW winding in SVG (Y-down) coords."""
    area = 0.0
    n = len(face_verts)
    for i in range(n):
        x1, y1 = coords[face_verts[i]]
        x2, y2 = coords[face_verts[(i + 1) % n]]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def vertices_vertices_to_faces_vertices(graph):
    """
    Trace all interior faces of the planar graph and store them in
    graph['faces_vertices'].  The outer (infinite) face is excluded.
    Requires graph['vertices_vertices'] to already be populated and sorted.
    Modifies graph in-place.
    """
    vv = graph["vertices_vertices"]
    coords = graph["vertices_coords"]
    n = len(vv)

    visited = set()
    faces = []

    for start_u in range(n):
        for start_v in vv[start_u]:
            if (start_u, start_v) in visited:
                continue

            # Trace the face starting with half-edge (start_u → start_v)
            face = []
            u, v = start_u, start_v

            while True:
                he = (u, v)
                if he in visited:
                    break
                visited.add(he)
                face.append(u)

                neighbors = vv[v]
                if not neighbors:
                    break
                try:
                    idx = neighbors.index(u)
                except ValueError:
                    break
                # Use (idx - 1) so interior faces wind CW on screen
                # (positive shoelace area in SVG Y-down), matching the FOLD
                # library convention.  The outer/infinite face winds CCW and
                # therefore has negative area, which we drop below.
                w = neighbors[(idx - 1) % len(neighbors)]
                u, v = v, w

            if len(face) >= 3:
                faces.append(face)

    # Drop the outer (infinite) face: it has negative shoelace area in
    # SVG Y-down coordinates (CW on screen = positive area for interior faces).
    faces = [f for f in faces if _signed_area(coords, f) > 0]

    graph["faces_vertices"] = faces


def faces_vertices_to_faces_edges(graph):
    """
    For each face, record the edge index for every consecutive vertex pair.
    Populates graph['faces_edges'].
    Modifies graph in-place.
    """
    # Build a fast lookup: (v_a, v_b) → edge index  (both orderings)
    edge_map = {}
    for i, (v1, v2) in enumerate(graph["edges_vertices"]):
        edge_map[(v1, v2)] = i
        edge_map[(v2, v1)] = i

    faces_edges = []
    for face in graph["faces_vertices"]:
        m = len(face)
        fe = [edge_map.get((face[i], face[(i + 1) % m]), -1) for i in range(m)]
        faces_edges.append(fe)

    graph["faces_edges"] = faces_edges


# ---------------------------------------------------------------------------
# Bonus: derive vertices_faces and edges_faces (not in original JS pipeline
# but useful for complete FOLD output).
# ---------------------------------------------------------------------------

def compute_vertices_faces(graph):
    n = len(graph["vertices_coords"])
    vf = [[] for _ in range(n)]
    for fi, face in enumerate(graph["faces_vertices"]):
        for v in face:
            vf[v].append(fi)
    graph["vertices_faces"] = vf


def compute_edges_faces(graph):
    n = len(graph["edges_vertices"])
    ef = [[] for _ in range(n)]
    for fi, face_edges in enumerate(graph["faces_edges"]):
        for e in face_edges:
            if e >= 0:
                ef[e].append(fi)
    graph["edges_faces"] = ef


def compute_edges_length(graph):
    coords = graph["vertices_coords"]
    graph["edges_length"] = [
        math.sqrt(
            (coords[v2][0] - coords[v1][0]) ** 2 +
            (coords[v2][1] - coords[v1][1]) ** 2
        )
        for v1, v2 in graph["edges_vertices"]
    ]
