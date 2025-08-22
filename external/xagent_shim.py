"""
Shim to alias the upstream 'XAgent' package (capital X) as 'xagent'.
Ensures submodules like xagent.controllers.* resolve correctly.
"""
import importlib
import sys
import pkgutil

try:
    # Import the top-level XAgent package
    XAgent_pkg = importlib.import_module("XAgent")
    sys.modules["xagent"] = XAgent_pkg

    # Auto-discover all submodules under XAgent
    for _, modname, ispkg in pkgutil.walk_packages(XAgent_pkg.__path__, XAgent_pkg.__name__ + "."):
        try:
            mod = importlib.import_module(modname)
            # Replace "XAgent" prefix with "xagent"
            alias = modname.replace("XAgent", "xagent", 1)
            sys.modules[alias] = mod
        except Exception:
            # Ignore failed submodule imports
            continue

except ImportError:
    # If XAgent not installed/cloned, leave it alone
    pass

