/* convert images into FOLD file format.
more info at https://github.com/robbykraft/tofold
more info on the FOLD format https://github.com/edemaine/fold
(c) Robby Kraft, MIT License */

(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define(factory) :
  (global.tofold = factory());
}(this, (function () { 'use strict';

  function _typeof(obj) {
    if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") {
      _typeof = function (obj) {
        return typeof obj;
      };
    } else {
      _typeof = function (obj) {
        return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj;
      };
    }

    return _typeof(obj);
  }

  function _toConsumableArray(arr) {
    return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread();
  }

  function _arrayWithoutHoles(arr) {
    if (Array.isArray(arr)) {
      for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) arr2[i] = arr[i];

      return arr2;
    }
  }

  function _iterableToArray(iter) {
    if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter);
  }

  function _nonIterableSpread() {
    throw new TypeError("Invalid attempt to spread non-iterable instance");
  }

  var isBrowser = typeof window !== "undefined" && typeof window.document !== "undefined";
  var isNode = typeof process !== "undefined" && process.versions != null && process.versions.node != null;
  var isWebWorker = (typeof self === "undefined" ? "undefined" : _typeof(self)) === "object" && self.constructor && self.constructor.name === "DedicatedWorkerGlobalScope";

  var htmlString = "<!DOCTYPE html><title>a</title>";
  var win = !isNode && isBrowser ? window : {};

  if (isNode) {
    var _require = require("xmldom"),
        DOMParser = _require.DOMParser,
        XMLSerializer = _require.XMLSerializer;

    win.DOMParser = DOMParser;
    win.XMLSerializer = XMLSerializer;
    win.document = new DOMParser().parseFromString(htmlString, "text/html");
  }

  var css_colors = {
    "black": "#000000",
    "silver": "#c0c0c0",
    "gray": "#808080",
    "white": "#ffffff",
    "maroon": "#800000",
    "red": "#ff0000",
    "purple": "#800080",
    "fuchsia": "#ff00ff",
    "green": "#008000",
    "lime": "#00ff00",
    "olive": "#808000",
    "yellow": "#ffff00",
    "navy": "#000080",
    "blue": "#0000ff",
    "teal": "#008080",
    "aqua": "#00ffff",
    "orange": "#ffa500",
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "blanchedalmond": "#ffebcd",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgreen": "#006400",
    "darkgrey": "#a9a9a9",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "greenyellow": "#adff2f",
    "grey": "#808080",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lavenderblush": "#fff0f5",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgray": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "oldlace": "#fdf5e6",
    "olivedrab": "#6b8e23",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "whitesmoke": "#f5f5f5",
    "yellowgreen": "#9acd32"
  };

  var css_color_names = Object.keys(css_colors);

  var hexToComponents = function hexToComponents(h) {
    var r = 0;
    var g = 0;
    var b = 0;
    var a = 255;

    if (h.length === 4) {
      r = "0x".concat(h[1]).concat(h[1]);
      g = "0x".concat(h[2]).concat(h[2]);
      b = "0x".concat(h[3]).concat(h[3]);
    } else if (h.length === 7) {
      r = "0x".concat(h[1]).concat(h[2]);
      g = "0x".concat(h[3]).concat(h[4]);
      b = "0x".concat(h[5]).concat(h[6]);
    } else if (h.length === 5) {
      r = "0x".concat(h[1]).concat(h[1]);
      g = "0x".concat(h[2]).concat(h[2]);
      b = "0x".concat(h[3]).concat(h[3]);
      a = "0x".concat(h[4]).concat(h[4]);
    } else if (h.length === 9) {
      r = "0x".concat(h[1]).concat(h[2]);
      g = "0x".concat(h[3]).concat(h[4]);
      b = "0x".concat(h[5]).concat(h[6]);
      a = "0x".concat(h[7]).concat(h[8]);
    }

    return [+(r / 255), +(g / 255), +(b / 255), +(a / 255)];
  };

  var color_to_assignment = function color_to_assignment(string) {
    if (string == null || typeof string !== "string") {
      return "U";
    }

    var c = [0, 0, 0, 1];

    if (string[0] === "#") {
      c = hexToComponents(string);
    } else if (css_color_names.indexOf(string) !== -1) {
      c = hexToComponents(css_colors[string]);
    }

    var ep = 0.05;

    if (c[0] < ep && c[1] < ep && c[2] < ep) {
      return "U";
    }

    if (c[0] > c[1] && c[0] - c[2] > ep) {
      return "M";
    }

    if (c[2] > c[1] && c[2] - c[0] > ep) {
      return "V";
    }

    return "U";
  };

  var EPSILON = 1e-6;

  var magnitude = function magnitude(v) {
    var sum = v.map(function (component) {
      return component * component;
    }).reduce(function (prev, curr) {
      return prev + curr;
    }, 0);
    return Math.sqrt(sum);
  };

  var normalize = function normalize(v) {
    var m = magnitude(v);
    return m === 0 ? v : v.map(function (c) {
      return c / m;
    });
  };

  var equivalent = function equivalent(a, b) {
    var epsilon = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : EPSILON;

    for (var i = 0; i < a.length; i += 1) {
      if (Math.abs(a[i] - b[i]) > epsilon) {
        return false;
      }
    }

    return true;
  };

  var edge_edge_comp_exclusive = function edge_edge_comp_exclusive(t0, t1) {
    return t0 > EPSILON && t0 < 1 - EPSILON && t1 > EPSILON && t1 < 1 - EPSILON;
  };

  var intersection_function = function intersection_function(aPt, aVec, bPt, bVec, compFunc) {
    var epsilon = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : EPSILON;

    function det(a, b) {
      return a[0] * b[1] - b[0] * a[1];
    }

    var denominator0 = det(aVec, bVec);

    if (Math.abs(denominator0) < epsilon) {
      return undefined;
    }

    var denominator1 = -denominator0;
    var numerator0 = det([bPt[0] - aPt[0], bPt[1] - aPt[1]], bVec);
    var numerator1 = det([aPt[0] - bPt[0], aPt[1] - bPt[1]], aVec);
    var t0 = numerator0 / denominator0;
    var t1 = numerator1 / denominator1;

    if (compFunc(t0, t1, epsilon)) {
      return [aPt[0] + aVec[0] * t0, aPt[1] + aVec[1] * t0];
    }

    return undefined;
  };

  var edge_edge_exclusive = function edge_edge_exclusive(a0, a1, b0, b1, epsilon) {
    var aVec = [a1[0] - a0[0], a1[1] - a0[1]];
    var bVec = [b1[0] - b0[0], b1[1] - b0[1]];
    return intersection_function(a0, aVec, b0, bVec, edge_edge_comp_exclusive, epsilon);
  };

  var point_on_edge_exclusive = function point_on_edge_exclusive(point, edge0, edge1) {
    var epsilon = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : EPSILON;
    var edge0_1 = [edge0[0] - edge1[0], edge0[1] - edge1[1]];
    var edge0_p = [edge0[0] - point[0], edge0[1] - point[1]];
    var edge1_p = [edge1[0] - point[0], edge1[1] - point[1]];
    var dEdge = Math.sqrt(edge0_1[0] * edge0_1[0] + edge0_1[1] * edge0_1[1]);
    var dP0 = Math.sqrt(edge0_p[0] * edge0_p[0] + edge0_p[1] * edge0_p[1]);
    var dP1 = Math.sqrt(edge1_p[0] * edge1_p[0] + edge1_p[1] * edge1_p[1]);
    return Math.abs(dEdge - dP0 - dP1) < epsilon;
  };

  var math = {
    core: {
      EPSILON: EPSILON,
      magnitude: magnitude,
      normalize: normalize,
      equivalent: equivalent,
      point_on_edge_exclusive: point_on_edge_exclusive,
      intersection: {
        edge_edge_exclusive: edge_edge_exclusive
      }
    }
  };

  var max_array_length = function max_array_length() {
    for (var _len = arguments.length, arrays = new Array(_len), _key = 0; _key < _len; _key++) {
      arrays[_key] = arguments[_key];
    }

    return Math.max.apply(Math, _toConsumableArray(arrays.filter(function (el) {
      return el !== undefined;
    }).map(function (el) {
      return el.length;
    })));
  };

  var vertices_count = function vertices_count(_ref) {
    var vertices_coords = _ref.vertices_coords,
        vertices_faces = _ref.vertices_faces,
        vertices_vertices = _ref.vertices_vertices;
    return max_array_length([], vertices_coords, vertices_faces, vertices_vertices);
  };

  var edges_count = function edges_count(_ref2) {
    var edges_vertices = _ref2.edges_vertices,
        edges_faces = _ref2.edges_faces;
    return max_array_length([], edges_vertices, edges_faces);
  };

  var faces_count = function faces_count(_ref3) {
    var faces_vertices = _ref3.faces_vertices,
        faces_edges = _ref3.faces_edges;
    return max_array_length([], faces_vertices, faces_edges);
  };

  var get_geometry_length = {
    vertices: vertices_count,
    edges: edges_count,
    faces: faces_count
  };

  var remove_geometry_key_indices = function remove_geometry_key_indices(graph, key, removeIndices) {
    var geometry_array_size = get_geometry_length[key](graph);
    var removes = Array(geometry_array_size).fill(false);
    removeIndices.forEach(function (v) {
      removes[v] = true;
    });
    var s = 0;
    var index_map = removes.map(function (remove) {
      return remove ? --s : s;
    });

    if (removeIndices.length === 0) {
      return index_map;
    }

    var prefix = "".concat(key, "_");
    var suffix = "_".concat(key);
    var graph_keys = Object.keys(graph);
    var prefixKeys = graph_keys.map(function (str) {
      return str.substring(0, prefix.length) === prefix ? str : undefined;
    }).filter(function (str) {
      return str !== undefined;
    });
    var suffixKeys = graph_keys.map(function (str) {
      return str.substring(str.length - suffix.length, str.length) === suffix ? str : undefined;
    }).filter(function (str) {
      return str !== undefined;
    });
    suffixKeys.forEach(function (sKey) {
      return graph[sKey].forEach(function (_, i) {
        return graph[sKey][i].forEach(function (v, j) {
          graph[sKey][i][j] += index_map[v];
        });
      });
    });
    prefixKeys.forEach(function (pKey) {
      graph[pKey] = graph[pKey].filter(function (_, i) {
        return !removes[i];
      });
    });
    return index_map;
  };

  var edges_vertices_equivalent = function edges_vertices_equivalent(a, b) {
    return a[0] === b[0] && a[1] === b[1] || a[0] === b[1] && a[1] === b[0];
  };

  var make_edges_collinearVertices = function make_edges_collinearVertices(_ref) {
    var vertices_coords = _ref.vertices_coords,
        edges_vertices = _ref.edges_vertices;
    var epsilon = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : math.core.EPSILON;
    var edges = edges_vertices.map(function (ev) {
      return ev.map(function (v) {
        return vertices_coords[v];
      });
    });
    return edges.map(function (e) {
      return vertices_coords.filter(function (v) {
        return math.core.point_on_edge_exclusive(v, e[0], e[1], epsilon);
      });
    });
  };

  var make_edges_alignment = function make_edges_alignment(_ref2) {
    var vertices_coords = _ref2.vertices_coords,
        edges_vertices = _ref2.edges_vertices;
    var edges = edges_vertices.map(function (ev) {
      return ev.map(function (v) {
        return vertices_coords[v];
      });
    });
    var edges_vector = edges.map(function (e) {
      return [e[1][0] - e[0][0], e[1][1] - e[0][1]];
    });
    var edges_magnitude = edges_vector.map(function (e) {
      return Math.sqrt(e[0] * e[0] + e[1] * e[1]);
    });
    var edges_normalized = edges_vector.map(function (e, i) {
      return [e[0] / edges_magnitude[i], e[1] / edges_magnitude[i]];
    });
    return edges_normalized.map(function (e) {
      return Math.abs(e[0]) > 0.707;
    });
  };

  var make_edges_intersections = function make_edges_intersections(_ref3) {
    var vertices_coords = _ref3.vertices_coords,
        edges_vertices = _ref3.edges_vertices;
    var epsilon = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : math.core.EPSILON;
    var edge_count = edges_vertices.length;
    var edges = edges_vertices.map(function (ev) {
      return ev.map(function (v) {
        return vertices_coords[v];
      });
    });
    var crossings = Array.from(Array(edge_count - 1)).map(function () {
      return [];
    });

    for (var i = 0; i < edges.length - 1; i += 1) {
      for (var j = i + 1; j < edges.length; j += 1) {
        crossings[i][j] = math.core.intersection.edge_edge_exclusive(edges[i][0], edges[i][1], edges[j][0], edges[j][1], epsilon);
      }
    }

    var edges_intersections = Array.from(Array(edge_count)).map(function () {
      return [];
    });

    for (var _i = 0; _i < edges.length - 1; _i += 1) {
      for (var _j = _i + 1; _j < edges.length; _j += 1) {
        if (crossings[_i][_j] != null) {
          edges_intersections[_i].push(crossings[_i][_j]);

          edges_intersections[_j].push(crossings[_i][_j]);
        }
      }
    }

    return edges_intersections;
  };

  var fragment = function fragment(graph) {
    var epsilon = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : math.core.EPSILON;

    var horizSort = function horizSort(a, b) {
      return a[0] - b[0];
    };

    var vertSort = function vertSort(a, b) {
      return a[1] - b[1];
    };

    var edges_alignment = make_edges_alignment(graph);
    var edges = graph.edges_vertices.map(function (ev) {
      return ev.map(function (v) {
        return graph.vertices_coords[v];
      });
    });
    edges.forEach(function (e, i) {
      return e.sort(edges_alignment[i] ? horizSort : vertSort);
    });
    var edges_intersections = make_edges_intersections(graph, epsilon);
    var edges_collinearVertices = make_edges_collinearVertices(graph, epsilon);
    var new_edges_vertices = edges_intersections.map(function (a, i) {
      return a.concat(edges_collinearVertices[i]);
    });
    new_edges_vertices.forEach(function (e, i) {
      return e.sort(edges_alignment[i] ? horizSort : vertSort);
    });
    var new_edges = new_edges_vertices.map(function (ev) {
      return Array.from(Array(ev.length - 1)).map(function (_, i) {
        return [ev[i], ev[i + 1]];
      });
    });
    new_edges = new_edges.map(function (edgeGroup) {
      return edgeGroup.filter(function (e) {
        return false === e.map(function (_, i) {
          return Math.abs(e[0][i] - e[1][i]) < epsilon;
        }).reduce(function (a, b) {
          return a && b;
        }, true);
      });
    });
    var edge_map = new_edges.map(function (edge, i) {
      return edge.map(function () {
        return i;
      });
    }).reduce(function (a, b) {
      return a.concat(b);
    }, []);
    var vertices_coords = new_edges.map(function (edge) {
      return edge.reduce(function (a, b) {
        return a.concat(b);
      }, []);
    }).reduce(function (a, b) {
      return a.concat(b);
    }, []);
    var counter = 0;
    var edges_vertices = new_edges.map(function (edge) {
      return edge.map(function () {
        return [counter++, counter++];
      });
    }).reduce(function (a, b) {
      return a.concat(b);
    }, []);
    var vertices_equivalent = Array.from(Array(vertices_coords.length)).map(function () {
      return [];
    });

    for (var i = 0; i < vertices_coords.length - 1; i += 1) {
      for (var j = i + 1; j < vertices_coords.length; j += 1) {
        vertices_equivalent[i][j] = math.core.equivalent(vertices_coords[i], vertices_coords[j], epsilon);
      }
    }

    var vertices_map = vertices_coords.map(function () {
      return undefined;
    });
    vertices_equivalent.forEach(function (row, i) {
      return row.forEach(function (eq, j) {
        if (eq) {
          vertices_map[j] = vertices_map[i] === undefined ? i : vertices_map[i];
        }
      });
    });
    var vertices_remove = vertices_map.map(function (m) {
      return m !== undefined;
    });
    vertices_map.forEach(function (map, i) {
      if (map === undefined) {
        vertices_map[i] = i;
      }
    });
    edges_vertices.forEach(function (edge, i) {
      return edge.forEach(function (v, j) {
        edges_vertices[i][j] = vertices_map[v];
      });
    });
    var edges_equivalent = Array.from(Array(edges_vertices.length)).map(function () {
      return [];
    });

    for (var _i2 = 0; _i2 < edges_vertices.length - 1; _i2 += 1) {
      for (var _j2 = _i2 + 1; _j2 < edges_vertices.length; _j2 += 1) {
        edges_equivalent[_i2][_j2] = edges_vertices_equivalent(edges_vertices[_i2], edges_vertices[_j2]);
      }
    }

    var edges_map = edges_vertices.map(function () {
      return undefined;
    });
    edges_equivalent.forEach(function (row, i) {
      return row.forEach(function (eq, j) {
        if (eq) {
          edges_map[i] = edges_map[j] === undefined ? j : edges_map[j];
        }
      });
    });
    var edges_dont_remove = edges_map.map(function (m) {
      return m === undefined;
    });
    edges_map.forEach(function (map, i) {
      if (map === undefined) {
        edges_map[i] = i;
      }
    });
    var edges_vertices_cl = edges_vertices.filter(function (_, i) {
      return edges_dont_remove[i];
    });
    var edge_map_cl = edge_map.filter(function (_, i) {
      return edges_dont_remove[i];
    });
    var flat = {
      vertices_coords: vertices_coords,
      edges_vertices: edges_vertices_cl
    };

    if ("edges_assignment" in graph === true) {
      flat.edges_assignment = edge_map_cl.map(function (i) {
        return graph.edges_assignment[i];
      });
    }

    if ("edges_foldAngle" in graph === true) {
      flat.edges_foldAngle = edge_map_cl.map(function (i) {
        return graph.edges_foldAngle[i];
      });
    }

    var vertices_remove_indices = vertices_remove.map(function (rm, i) {
      return rm ? i : undefined;
    }).filter(function (i) {
      return i !== undefined;
    });
    remove_geometry_key_indices(flat, "vertices", vertices_remove_indices);
    return flat;
  };

  var make_vertex_pair_to_edge_map = function make_vertex_pair_to_edge_map(_ref) {
    var edges_vertices = _ref.edges_vertices;
    var map = {};
    edges_vertices.map(function (ev) {
      return ev.sort(function (a, b) {
        return a - b;
      }).join(" ");
    }).forEach(function (key, i) {
      map[key] = i;
    });
    return map;
  };

  var boundary_vertex_walk = function boundary_vertex_walk(_ref, startIndex, neighbor_index) {
    var vertices_vertices = _ref.vertices_vertices;
    var walk = [startIndex, neighbor_index];

    while (walk[0] !== walk[walk.length - 1]) {
      var next_v_v = vertices_vertices[walk[walk.length - 1]];
      var next_i_v_v = next_v_v.indexOf(walk[walk.length - 2]);
      var next_v = next_v_v[(next_i_v_v + 1) % next_v_v.length];
      walk.push(next_v);
    }

    walk.pop();
    return walk;
  };

  var search_boundary = function search_boundary(graph) {
    if (graph.vertices_coords == null || graph.vertices_coords.length < 1) {
      return [];
    }

    var startIndex = 0;

    for (var i = 1; i < graph.vertices_coords.length; i += 1) {
      if (graph.vertices_coords[i][1] < graph.vertices_coords[startIndex][1]) {
        startIndex = i;
      }
    }

    if (startIndex === -1) {
      return [];
    }

    var adjacent = graph.vertices_vertices[startIndex];
    var adjacent_vectors = adjacent.map(function (a) {
      return [graph.vertices_coords[a][0] - graph.vertices_coords[startIndex][0], graph.vertices_coords[a][1] - graph.vertices_coords[startIndex][1]];
    });
    var adjacent_dot_products = adjacent_vectors.map(function (v) {
      return math.core.normalize(v);
    }).map(function (v) {
      return v[0];
    });
    var neighbor_index = -1;
    var counter_max = -Infinity;

    for (var _i = 0; _i < adjacent_dot_products.length; _i += 1) {
      if (adjacent_dot_products[_i] > counter_max) {
        neighbor_index = _i;
        counter_max = adjacent_dot_products[_i];
      }
    }

    var vertices = boundary_vertex_walk(graph, startIndex, adjacent[neighbor_index]);
    var edgeMap = make_vertex_pair_to_edge_map(graph);
    var vertices_pairs = vertices.map(function (_, i, arr) {
      return [arr[i], arr[(i + 1) % arr.length]].sort(function (a, b) {
        return a - b;
      }).join(" ");
    });
    var edges = vertices_pairs.map(function (p) {
      return edgeMap[p];
    });
    return edges;
  };

  var Segmentize = win.Segmentize || require("svg-segmentize");

  var FOLD = win.FOLD || require("fold");

  var assignment_foldAngle = {
    V: 180,
    v: 180,
    M: -180,
    m: -180
  };

  var assignment_to_foldAngle = function assignment_to_foldAngle(assignment) {
    return assignment_foldAngle[assignment] || 0;
  };

  var emptyFOLD = function emptyFOLD() {
    return {
      file_spec: 1.1,
      file_creator: "Rabbit Ear",
      file_classes: ["singleModel"],
      frame_title: "",
      frame_classes: ["creasePattern"],
      frame_attributes: ["2D"],
      vertices_coords: [],
      vertices_vertices: [],
      vertices_faces: [],
      edges_vertices: [],
      edges_faces: [],
      edges_assignment: [],
      edges_foldAngle: [],
      edges_length: [],
      faces_vertices: [],
      faces_edges: []
    };
  };














  
  var svg_to_fold = function svg_to_fold(svg, options) {
    var pre_frag = emptyFOLD();
    var v0 = pre_frag.vertices_coords.length;
    var segments = Segmentize(svg);
    pre_frag.vertices_coords = segments.map(function (s) {
      return [[s[0], s[1]], [s[2], s[3]]];
    }).reduce(function (a, b) {
      return a.concat(b);
    }, pre_frag.vertices_coords);
    pre_frag.edges_vertices = segments.map(function (_, i) {
      return [v0 + i * 2, v0 + i * 2 + 1];
    });
    pre_frag.edges_assignment = segments.map(function (a) {
      return a[4];
    }).map(function (attrs) {
      return attrs != null ? color_to_assignment(attrs.stroke) : "U";
    });
    var graph = fragment(pre_frag, options.epsilon);
    FOLD.convert.edges_vertices_to_vertices_vertices_sorted(graph);
    FOLD.convert.vertices_vertices_to_faces_vertices(graph);
    FOLD.convert.faces_vertices_to_faces_edges(graph);
    graph.edges_foldAngle = graph.edges_assignment.map(function (a) {
      return assignment_to_foldAngle(a);
    });

    if (options.boundary !== false) {
      search_boundary(graph).forEach(function (edgeIndex) {
        graph.edges_assignment[edgeIndex] = "B";
      });
    }

    return graph;
  };

  var SVGtoFOLD = function SVGtoFOLD(input) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

    if (typeof input === "string") {
      var svg = new win.DOMParser().parseFromString(input, "text/xml").documentElement;
      return svg_to_fold(svg, options);
    }

    return svg_to_fold(input, options);
  };

  SVGtoFOLD.core = {
    segmentize: function segmentize() {},
    fragment: fragment
  };

  return SVGtoFOLD;

})));
