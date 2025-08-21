"""
XAgent adapter for team-of-ai-agents

Purpose:
- Replace LangChain ReAct agent with OpenBMB XAgent
- Provide a drop-in adapter exposing .invoke() and .run()
"""

from typing import Any, Dict, Iterable, List, Optional

# Import XAgent APIs
try:
    from xagent.controller import Controller
    from xagent.config import Config
except ImportError:
    raise ImportError("XAgent is not installed. Run: pip install git+https://github.com/OpenBMB/XAgent.git")

class XAgentAdapter:
    """Adapter wrapper around OpenBMB XAgent."""

    def __init__(self, model: Optional[str] = "gpt-4", tools: Optional[Iterable] = None, prompt: Optional[str] = None):
        """
        model: model name or id (depends on backend config)
        tools: list of tool objects from L3AGI to be converted
        prompt: optional initial system prompt
        """
        self.model = model
        self.tools = tools or []
        self.prompt = prompt or "You are XAgent integrated into L3AGI."

        # Initialize XAgent config and controller
        self.config = Config(model=self.model)
        self.controller = Controller(config=self.config)

    def _convert_tools(self, tools: Iterable) -> List[Dict[str, Any]]:
        """Convert L3AGI tool specs into XAgent-compatible format."""
        converted = []
        for t in tools:
            converted.append({
                "name": getattr(t, "name", str(t)),
                "description": getattr(t, "description", ""),
                # TODO: Map to callable if needed
            })
        return converted

    def invoke(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Run XAgent with input_text and return dict similar to LangChain ReAct agent.
        """
        x_tools = self._convert_tools(self.tools)

        # Example: call XAgent controller
        try:
            result = self.controller.run(input_text, tools=x_tools)
            output_text = result.get("output", str(result))
        except Exception as e:
            output_text = f"[xagent-error] {e}"
            result = {}

        return {"output": output_text, "actions": [], "raw": result}

    def run(self, input_text: str, **kwargs):
        """Alias for invoke() to be compatible with older code."""
        return self.invoke(input_text, **kwargs)
