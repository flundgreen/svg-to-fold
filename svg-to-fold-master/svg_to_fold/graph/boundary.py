"""
Detect the outer boundary polygon of a planar crease-pattern graph.

Ported from src/graph/boundary.js.

The boundary is found by:
  1. Picking the vertex with the smallest Y coordinate (topmost in SVG).
  2. From that vertex, choosing the neighbour with the largest dot-product
     with [1, 0] (the rightmost direction).
  3. Walking around the boundary using the +1 step in the sorted
     vertices_vertices adjacency list (same convention as face traversal).

Returns a list of edge indices that form the boundary polygon.
"""

from .math_utils import normalize


def _make_vertex_pair_to_edge_map(graph):
    """Build {min_v space max_v: edge_index} dict for O(1) edge lookup."""
    edge_map = {}
    for i, (v1, v2) in enumerate(graph["edges_vertices"]):
        key = "{} {}".format(*sorted([v1, v2]))
        edge_map[key] = i
    return edge_map


def _boundary_vertex_walk(vertices_vertices, start_index, neighbor_index):
    """Walk the boundary starting at start_index → neighbor_index."""
    walk = [start_index, neighbor_index]
    while walk[0] != walk[-1]:
        current = walk[-1]
        prev = walk[-2]
        vv = vertices_vertices[current]
        prev_pos = vv.index(prev)
        next_v = vv[(prev_pos + 1) % len(vv)]
        walk.append(next_v)
    walk.pop()  # remove the duplicate closing vertex
    return walk


def find_boundary(graph):
    """
    Return a list of edge indices forming the outer boundary of *graph*.
    Returns [] if the graph has no vertices or the boundary cannot be found.
    Requires graph['vertices_coords'] and graph['vertices_vertices'].
    """
    coords = graph.get("vertices_coords", [])
    vv = graph.get("vertices_vertices", [])

    if not coords:
        return []

    # 1. Find the vertex with the smallest Y (topmost on screen)
    start_index = min(range(len(coords)), key=lambda i: coords[i][1])

    adjacent = vv[start_index]
    if not adjacent:
        return []

    # 2. Pick the neighbour in the most +X direction (dot with [1, 0])
    def dot_x(nb):
        vec = [coords[nb][0] - coords[start_index][0],
               coords[nb][1] - coords[start_index][1]]
        nv = normalize(vec)
        return nv[0]

    best_neighbor = max(adjacent, key=dot_x)

    # 3. Walk the boundary
    vertices = _boundary_vertex_walk(vv, start_index, best_neighbor)

    # 4. Convert vertex walk to edge indices
    edge_map = _make_vertex_pair_to_edge_map(graph)
    edges = []
    n = len(vertices)
    for i in range(n):
        v1, v2 = vertices[i], vertices[(i + 1) % n]
        key = "{} {}".format(*sorted([v1, v2]))
        if key in edge_map:
            edges.append(edge_map[key])

    return edges
