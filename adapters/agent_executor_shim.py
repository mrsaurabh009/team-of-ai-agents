
"""
AgentExecutorShim: small compatibility shim to replace LangChain ReAct / AgentExecutor
with your XAgentAdapter. Change only imports that create agents to use this shim.

Supports:
 - .run(text) -> returns text
 - .invoke({"input": text}) -> returns dict with "output"
 - callable(agent)("text") -> returns text
"""

from typing import Any, Dict, Iterable, Optional
from .xagent_adapter import XAgentAdapter

class AgentExecutorShim:
    def __init__(self, llm: Optional[Any] = None, tools: Optional[Iterable] = None,
                 prompt: Optional[str] = None, model: Optional[str] = None, **kwargs):
        """
        Accepts common params caller might pass (llm, tools, prompt).
        Prefer passing `model` if you want to select a model string for XAgent.
        """
        # Derive a model name if possible
        model_name = model or (getattr(llm, "model_name", None) if llm is not None else None) or "gpt-4"
        self.adapter = XAgentAdapter(model=model_name, tools=tools, prompt=prompt)

    def run(self, input_text: str, **kwargs) -> str:
        """Return textual output (most callers call .run to get string)."""
        res = self.adapter.run(input_text, **kwargs)
        if isinstance(res, dict):
            return res.get("output", str(res))
        return str(res)

    def invoke(self, input_obj: Any, **kwargs) -> Dict[str, Any]:
        """
        Accepts dicts like {'input': '...'} or a plain string.
        Returns a dict with at least 'output' key.
        """
        if isinstance(input_obj, dict):
            text = input_obj.get("input") or input_obj.get("text") or ""
        else:
            text = str(input_obj)
        res = self.adapter.invoke(text, **kwargs)
        if isinstance(res, dict):
            return res
        return {"output": str(res), "raw": res}

    def __call__(self, *args, **kwargs):
        """Allow agent('text') usage returning string."""
        if args:
            return self.run(args[0])
        if "input" in kwargs:
            return self.run(kwargs["input"])
        return self.run("")
