"""
Generic removal of graph elements with index remapping.
Ported from src/graph/remove.js
"""


def _geometry_length(graph, key):
    """Return the count of elements for a given key (vertices/edges/faces)."""
    prefix = key + "_"
    suffix = "_" + key
    length = 0
    for k, v in graph.items():
        if (k.startswith(prefix) or k.endswith(suffix)) and isinstance(v, list):
            length = max(length, len(v))
    return length


def remove_geometry_key_indices(graph, key, remove_indices):
    """
    Remove elements identified by *remove_indices* from the graph.
    Updates both prefix arrays (e.g. vertices_coords) by filtering them, and
    suffix arrays (e.g. edges_vertices) by remapping their stored indices.

    Returns the index_map (shift values) for callers that need it.

    Usage:  remove_geometry_key_indices(graph, "vertices", [2, 6, 11])
    """
    count = _geometry_length(graph, key)
    removes = [False] * count
    for i in remove_indices:
        removes[i] = True

    # index_map[i] = how much index i shifts after removals (negative or zero)
    s = 0
    index_map = []
    for rm in removes:
        if rm:
            s -= 1
        index_map.append(s)

    if not remove_indices:
        return index_map

    prefix = key + "_"
    suffix = "_" + key
    prefix_keys = [k for k in graph if k.startswith(prefix)]
    suffix_keys = [k for k in graph if k.endswith(suffix)]

    # Suffix arrays: contents point to element indices — shift them
    for skey in suffix_keys:
        for i, row in enumerate(graph[skey]):
            for j, v in enumerate(row):
                graph[skey][i][j] = v + index_map[v]

    # Prefix arrays: filter out removed elements
    for pkey in prefix_keys:
        graph[pkey] = [v for i, v in enumerate(graph[pkey]) if not removes[i]]

    return index_map
