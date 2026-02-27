"""
Command-line interface for svg_to_fold.

Usage examples
--------------
  # Convert one file (output alongside input)
  python -m svg_to_fold crane.svg

  # Convert several files
  python -m svg_to_fold *.svg

  # Specify an output directory
  python -m svg_to_fold *.svg --output ./fold_files/

  # Convert all SVGs in a directory (recursively)
  python -m svg_to_fold --dir ./my_patterns/ --output ./fold_files/

  # Tune floating-point tolerance and skip boundary detection
  python -m svg_to_fold crane.svg --epsilon 1e-5 --no-boundary

  # Pretty-print output JSON
  python -m svg_to_fold crane.svg --pretty
"""

import argparse
import json
import os
import sys
import glob

from .converter import svg_to_fold


def _collect_svg_files(paths, recursive=False):
    """Expand a list of paths/globs into a deduplicated list of .svg files."""
    seen = set()
    files = []
    for p in paths:
        # Expand shell glob patterns (needed on Windows where the shell
        # doesn't expand them automatically)
        expanded = glob.glob(p, recursive=recursive) if ("*" in p or "?" in p) else [p]
        for f in expanded:
            f = os.path.abspath(f)
            if os.path.isfile(f) and f.lower().endswith(".svg") and f not in seen:
                seen.add(f)
                files.append(f)
    return files


def _collect_from_dir(directory, recursive=False):
    """Find all .svg files in *directory*."""
    files = []
    if recursive:
        for root, _dirs, filenames in os.walk(directory):
            for fname in filenames:
                if fname.lower().endswith(".svg"):
                    files.append(os.path.abspath(os.path.join(root, fname)))
    else:
        for fname in os.listdir(directory):
            if fname.lower().endswith(".svg"):
                files.append(os.path.abspath(os.path.join(directory, fname)))
    return sorted(files)


def _output_path(svg_path, output_dir):
    """Compute the .fold output path for a given .svg input path."""
    base = os.path.splitext(os.path.basename(svg_path))[0]
    out_dir = output_dir if output_dir else os.path.dirname(svg_path)
    return os.path.join(out_dir, base + ".fold")


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="svg_to_fold",
        description=(
            "Convert SVG crease-pattern files to FOLD format.\n\n"
            "Colour coding:\n"
            "  Red-dominant stroke  -> Mountain fold (M)\n"
            "  Blue-dominant stroke -> Valley fold   (V)\n"
            "  Other / black        -> Unassigned    (U)\n"
            "  Outer boundary       -> Boundary      (B)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE.svg",
        help="One or more SVG files (supports glob patterns).",
    )
    parser.add_argument(
        "--dir", "-d",
        metavar="DIRECTORY",
        help="Convert all SVG files in this directory.",
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=False,
        help="Recurse into sub-directories when using --dir.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="DIRECTORY",
        help=(
            "Directory for output .fold files.  "
            "Created automatically if it does not exist.  "
            "Defaults to the same directory as each input file."
        ),
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Floating-point tolerance for geometry tests (default: 1e-6).",
    )
    parser.add_argument(
        "--merge-tolerance",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help=(
            "Vertices within this many SVG px of each other are merged into one. "
            "Keeps the graph clean when the SVG editor rounds coordinates to integers. "
            "Default: 1.0.  Set to 0 to disable."
        ),
    )
    parser.add_argument(
        "--no-boundary",
        dest="boundary",
        action="store_false",
        default=True,
        help="Skip automatic boundary-edge detection.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="Pretty-print the JSON output (indented).",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        default=False,
        help="Suppress per-file progress messages.",
    )

    args = parser.parse_args(argv)

    # ------------------------------------------------------------------ #
    # Collect input files
    # ------------------------------------------------------------------ #
    svg_files = []

    if args.files:
        svg_files.extend(_collect_svg_files(args.files, recursive=args.recursive))

    if args.dir:
        if not os.path.isdir(args.dir):
            parser.error("--dir '{}' is not a directory.".format(args.dir))
        svg_files.extend(_collect_from_dir(args.dir, recursive=args.recursive))

    if not svg_files:
        parser.print_help()
        print("\nError: no SVG files found.", file=sys.stderr)
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    svg_files = [f for f in svg_files if not (f in seen or seen.add(f))]

    # ------------------------------------------------------------------ #
    # Prepare output directory
    # ------------------------------------------------------------------ #
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Convert
    # ------------------------------------------------------------------ #
    errors = []
    for svg_path in svg_files:
        out_path = _output_path(svg_path, args.output)
        try:
            fold_data = svg_to_fold(
                svg_path,
                epsilon=args.epsilon,
                boundary=args.boundary,
                merge_tolerance=args.merge_tolerance,
            )
            indent = 2 if args.pretty else None
            json_str = json.dumps(fold_data, indent=indent)
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(json_str)

            if not args.quiet:
                n_v = len(fold_data.get("vertices_coords", []))
                n_e = len(fold_data.get("edges_vertices", []))
                n_f = len(fold_data.get("faces_vertices", []))
                print(
                    "{svg} -> {fold}  "
                    "({v} vertices, {e} edges, {f} faces)".format(
                        svg=os.path.basename(svg_path),
                        fold=os.path.basename(out_path),
                        v=n_v, e=n_e, f=n_f,
                    )
                )

        except Exception as exc:  # noqa: BLE001
            msg = "ERROR: {} - {}".format(svg_path, exc)
            print(msg, file=sys.stderr)
            errors.append(msg)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    run()
