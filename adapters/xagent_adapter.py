from typing import Any, Dict, Iterable, List, Optional
import os
import sys

# Ensure external shims are loaded
import external.xagent_shim

# Import with lowercase alias (shim will redirect to XAgent)
try:
    from xagent.controllers.controller import Controller  # type: ignore
    from xagent.configs import Config  # type: ignore
except Exception as e:
    raise ImportError(
        f"XAgent (as xagent) could not be imported: {e}\n"
        "Fix by either:\n"
        "1) Installing properly: pip install git+https://github.com/OpenBMB/XAgent.git\n"
        "2) Using local clone: git clone https://github.com/OpenBMB/XAgent.git external/XAgent\n"
        "   Then run with: export PYTHONPATH=$PWD/external:$PYTHONPATH"
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
                }
            )
        return converted

    def invoke(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """Run XAgent with input_text and return a LangChain-like dict."""
        x_tools = self._convert_tools(self.tools)
        try:
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
