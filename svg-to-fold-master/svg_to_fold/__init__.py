"""
svg_to_fold — Convert SVG crease-pattern files to FOLD format.

Quick start
-----------
>>> from svg_to_fold import svg_to_fold
>>> fold_data = svg_to_fold("my_pattern.svg")

Command-line
------------
    python -m svg_to_fold file1.svg file2.svg ...
    python -m svg_to_fold --help
"""

from .converter import svg_to_fold

__all__ = ["svg_to_fold"]
__version__ = "1.0.0"
