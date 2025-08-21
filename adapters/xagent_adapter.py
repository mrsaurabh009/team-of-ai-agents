"""
adapters/xagent_adapter.py

Robust XAgent adapter for team-of-ai-agents.

This file tries multiple import strategies:
 - official install: `import xagent`
 - local checkout fallback: uses external/XAgent/xagent in the repo
"""

from typing import Any, Dict, Iterable, List, Optional
import os
import sys

# Attempt to import XAgent from normal site-packages first.
Controller = None
Config = None

try:
    # preferred import if the package is properly installed
    from xagent.controllers.controller import Controller  # type: ignore
    from xagent.configs import Config  # type: ignore
    _import_source = "site-packages (xagent)"
except Exception:
    # fallback: try to find external/XAgent/xagent inside this repo
    # compute candidate path relative to this file
    _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    _external_xagent = os.path.join(_repo_root, "external", "XAgent", "xagent")
    _external_link = os.path.join(_repo_root, "external", "xagent")

    # prefer the canonical cloned location external/XAgent/xagent
    if os.path.isdir(_external_xagent):
        if _external_xagent not in sys.path:
            sys.path.insert(0, _external_xagent)
        try:
            from controllers.controller import Controller  # type: ignore
            from configs import Config  # type: ignore
            # note: when importing directly from the xagent source path, imports are relative to that folder
            _import_source = "local external/XAgent/xagent"
        except Exception:
            Controller = None
            Config = None
    elif os.path.isdir(_external_link):
        # If you created a symlink external/xagent -> external/XAgent/xagent
        if _external_link not in sys.path:
            sys.path.insert(0, _external_link)
        try:
            from controllers.controller import Controller  # type: ignore
            from configs import Config  # type: ignore
            _import_source = "local external/xagent symlink"
        except Exception:
            Controller = None
            Config = None
    else:
        Controller = None
        Config = None

# If still not available, raise a helpful ImportError
if Controller is None or Config is None:
    raise ImportError(
        "XAgent module not found. Two options to fix:\n"
        "1) Install properly: `pip install -r requirements.txt` or\n"
        "   `pip install git+https://github.com/OpenBMB/XAgent.git`\n"
        "2) Use the local repo fallback (recommended for dev):\n"
        "   git clone https://github.com/OpenBMB/XAgent.git external/XAgent\n"
        "   (then ensure external/XAgent/xagent exists). You may also add:\n"
        "   export PYTHONPATH=$PWD/external:$PYTHONPATH\n"
        "After that re-run your script. (See README / RUN.md for instructions.)"
    )


class XAgentAdapter:
    """
    Adapter wrapper around OpenBMB XAgent.

    Provides:
      - invoke(input_text) -> dict: {'output': str, 'actions': [...], 'raw': ...}
      - run(input_text) -> str
    """

    def __init__(
        self,
        model: Optional[str] = "gpt-4",
        tools: Optional[Iterable] = None,
        prompt: Optional[str] = None,
    ):
        self.model = model
        self.tools = tools or []
        self.prompt = prompt or "You are XAgent integrated into L3AGI."

        try:
            # instantiate XAgent Config and Controller according to detected structure
            # If we imported from site-packages style, Config is the one from package namespace
            # If we imported by inserting external/xagent into sys.path, Config is also available
            self.config = Config(model=self.model)  # type: ignore
            self.controller = Controller(config=self.config)  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Failed to initialize XAgent Controller: {e}") from e

    def _convert_tools(self, tools: Iterable) -> List[Dict[str, Any]]:
        """Convert L3AGI tool specs into XAgent-compatible format (best-effort)."""
        converted: List[Dict[str, Any]] = []
        for t in tools:
            converted.append(
                {
                    "name": getattr(t, "name", str(t)),
                    "description": getattr(t, "description", ""),
                    # caller may need to bind callables manually
                }
            )
        return converted

    def invoke(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Run XAgent with input_text and return dict similar to LangChain ReAct agent.
        """
        x_tools = self._convert_tools(self.tools)
        try:
            # many versions of XAgent have `controller.run(prompt, tools=...)`
            result = self.controller.run(input_text, tools=x_tools)  # type: ignore
            if isinstance(result, dict):
                output_text = result.get("output", str(result))
            else:
                output_text = str(result)
                result = {"raw_result": result}
        except Exception as e:
            output_text = f"[xagent-error] {e}"
            result = {"error": str(e)}
        return {"output": output_text, "actions": [], "raw": result}

    def run(self, input_text: str, **kwargs) -> str:
        """Return only the textual output (compatibility alias)."""
        return self.invoke(input_text, **kwargs).get("output", "")
