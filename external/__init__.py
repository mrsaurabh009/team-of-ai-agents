"""
External dependencies bootstrapper.

This file ensures that the `xagent` package from external/XAgent is importable,
even though the upstream OpenBMB/XAgent repo is not properly packaged for pip.

Usage:
    import xagent
    from xagent.controllers.controller import Controller
"""

import os
import sys

# Path to the checked-out external XAgent repo
_xagent_path = os.path.join(os.path.dirname(__file__), "XAgent")

if os.path.isdir(os.path.join(_xagent_path, "xagent")):
    xagent_src = os.path.join(_xagent_path, "xagent")
    if xagent_src not in sys.path:
        sys.path.insert(0, xagent_src)
