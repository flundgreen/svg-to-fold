SVG to FOLD Converter
=====================

Converts SVG origami crease-pattern files into FOLD format (.fold).

FOLD is a JSON-based format that stores vertices, edges, faces, and fold
assignments for origami crease patterns.


REQUIREMENTS
------------
Python 3.8 or newer.

Run all commands from the svg-to-fold-master folder (the folder that
contains the svg_to_fold subfolder).


COLOUR CODING
-------------
The converter reads stroke colours from SVG lines to assign fold types:

  Red-dominant stroke  -> Mountain fold  (M)
  Blue-dominant stroke -> Valley fold    (V)
  Other / black        -> Unassigned     (U)
  Outer boundary       -> Boundary       (B)


BASIC COMMANDS
--------------

Convert a single file (output saved next to the input file):

  python -m svg_to_fold "SVG files/MyPattern.svg"


Convert a single file and save to a specific output folder:

  python -m svg_to_fold "SVG files/MyPattern.svg" --output "FOLD File Output"


Convert all SVG files in a folder:

  python -m svg_to_fold --dir "SVG files" --output "FOLD File Output"


Convert all SVG files in a folder and all its sub-folders:

  python -m svg_to_fold --dir "SVG files" --output "FOLD File Output" --recursive


OPTIONS
-------

--output DIRECTORY  (or -o)
    Folder where .fold files are saved.
    Created automatically if it does not exist.
    Default: same folder as the input SVG.

--merge-tolerance FLOAT
    Vertices within this many SVG pixels are merged into one vertex.
    Useful when the SVG editor rounds coordinates to whole numbers.
    Default: 1.0
    Set to 0 to disable merging.

    Example (tighter tolerance):
      python -m svg_to_fold MyPattern.svg --merge-tolerance 0.5

    Example (disable merging):
      python -m svg_to_fold MyPattern.svg --merge-tolerance 0

--epsilon FLOAT
    Floating-point tolerance used for intersection and deduplication tests.
    Default: 1e-6 (0.000001)
    Only change this if you are getting unexpected results.

    Example:
      python -m svg_to_fold MyPattern.svg --epsilon 1e-5

--no-boundary
    Skip automatic detection and labelling of boundary edges.
    By default the outer perimeter is labelled "B".

--pretty
    Write the output JSON with indentation so it is easier to read in a
    text editor.

    Example:
      python -m svg_to_fold MyPattern.svg --pretty

--quiet  (or -q)
    Do not print the per-file summary (vertices / edges / faces count).

--recursive  (or -r)
    When used with --dir, also search all sub-folders.


FULL EXAMPLES
-------------

Convert BirdFootTest.svg and save to the output folder:

  python -m svg_to_fold "SVG files/BirdFootTest.svg" --output "FOLD File Output"


Convert BloomY6.1V1.svg with default settings:

  python -m svg_to_fold "SVG files/BloomY6.1V1.svg" --output "FOLD File Output"


Convert BloomY6.1V1.svg with a custom merge tolerance and pretty output:

  python -m svg_to_fold "SVG files/BloomY6.1V1.svg" --output "FOLD File Output" --merge-tolerance 1.5 --pretty


Convert every SVG in the SVG files folder at once:

  python -m svg_to_fold --dir "SVG files" --output "FOLD File Output"
