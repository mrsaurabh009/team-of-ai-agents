"""
XAgent adapter for team-of-ai-agents

Purpose:
- Replace LangChain ReAct agent with OpenBMB XAgent
- Provide a drop-in adapter exposing .invoke() and .run()
"""

from typing import Any, Dict, Iterable, List, Optional

# Import XAgent APIs
try:
    from XAgent.controller import Controller  # Note: capital X
    from XAgent.config import Config
except ImportError as e:
    raise ImportError(
        "XAgent is not installed or cannot be imported. "
        "Run: pip install git+https://github.com/OpenBMB/XAgent.git"
    ) from e


class XAgentAdapter:
    """
    Adapter wrapper around OpenBMB XAgent.
    Exposes .invoke() and .run() methods for compatibility with LangChain-style agents.
    """

    def __init__(
        self,
        model: Optional[str] = "gpt-4",
        tools: Optional[Iterable] = None,
        prompt: Optional[str] = None,
    ):
        """
        Args:
            model: Model name or ID (depends on backend config).
            tools: Iterable of tool objects from L3AGI to be converted.
            prompt: Optional initial system prompt.
        """
        self.model = model
        self.tools = tools or []
        self.prompt = prompt or "You are XAgent integrated into L3AGI."

        # Initialize XAgent config and controller
        try:
            self.config = Config(model=self.model)
            self.controller = Controller(config=self.config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize XAgent Controller: {e}") from e

    def _convert_tools(self, tools: Iterable) -> List[Dict[str, Any]]:
        """Convert L3AGI tool specs into XAgent-compatible format."""
        converted = []
        for t in tools:
            converted.append(
                {
                    "name": getattr(t, "name", str(t)),
                    "description": getattr(t, "description", ""),
                    # TODO: Map to callable if needed
                }
            )
        return converted

    def invoke(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Run XAgent with input_text and return dict similar to LangChain ReAct agent.

        Returns:
            Dict with keys:
              - output: final text string
              - actions: list of actions (currently [])
              - raw: raw XAgent result
        """
        x_tools = self._convert_tools(self.tools)

        try:
            result = self.controller.run(input_text, tools=x_tools)
            if isinstance(result, dict):
                output_text = result.get("output", str(result))
            else:
                # fallback if controller.run returns a string or unknown type
                output_text = str(result)
                result = {"raw_result": result}
        except Exception as e:
            output_text = f"[xagent-error] {e}"
            result = {}

        return {"output": output_text, "actions": [], "raw": result}

    def run(self, input_text: str, **kwargs) -> str:
        """
        Alias for invoke(), returns only the output string.
        Kept for compatibility with older code expecting .run().
        """
        return self.invoke(input_text, **kwargs).get("output", "")
