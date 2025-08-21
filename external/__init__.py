"""
External dependencies bootstrapper.

Ensures external/XAgent/xagent is on sys.path if present.
"""

import os
import sys

_pkg_root = os.path.dirname(__file__)
_xagent_src = os.path.join(_pkg_root, "XAgent", "xagent")
_symlink_candidate = os.path.join(_pkg_root, "xagent")

if os.path.isdir(_xagent_src) and _xagent_src not in sys.path:
    sys.path.insert(0, _xagent_src)
elif os.path.isdir(_symlink_candidate) and _symlink_candidate not in sys.path:
    sys.path.insert(0, _symlink_candidate)
