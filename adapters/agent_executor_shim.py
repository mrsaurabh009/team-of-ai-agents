from typing import Any, Dict, Iterable, Optional, AsyncGenerator
from types import SimpleNamespace
import asyncio

from .xagent_adapter import XAgentAdapter


class AgentExecutorShim:
    """
    Compatibility shim so existing code calling AgentExecutor / ReAct-style APIs
    can work with XAgentAdapter.

    Provides:
      - run(input_text) -> str
      - invoke({"input": text}) -> {"output": ...}
      - __call__(text) -> str
      - astream_events({"input": text}) -> async generator of events (simulated)
    """

    def __init__(self, llm: Optional[Any] = None, tools: Optional[Iterable] = None,
                 prompt: Optional[str] = None, model: Optional[str] = None, **kwargs):
        model_name = model or (getattr(llm, "model_name", None) if llm else None) or "gpt-4"
        self.adapter = XAgentAdapter(model=model_name, tools=tools, prompt=prompt)

    def run(self, input_text: str, **kwargs) -> str:
        """Synchronous textual API for callers expecting a string."""
        res = self.adapter.run(input_text, **kwargs)
        if isinstance(res, dict):
            return res.get("output", str(res))
        return str(res)

    def invoke(self, input_obj: Any, **kwargs) -> Dict[str, Any]:
        """Return a dict, accepting either dict or plain string."""
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

    async def astream_events(self, input_obj: Any, version: str = "v1") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Simulated async streaming event generator to match the shape expected
        by the original conversational code. If XAgent supports streaming,
        adapt this method to use its streaming API. For now we call the adapter
        synchronously and yield a single 'on_chat_model_stream' chunk containing
        the full output.
        """
        if isinstance(input_obj, dict):
            text = input_obj.get("input") or input_obj.get("text") or ""
        else:
            text = str(input_obj)

        try:
            res = self.adapter.invoke(text)
        except Exception as e:
            # produce an error-like stream event to allow caller to handle errors
            await asyncio.sleep(0)
            yield {"event": "on_error", "data": {"error": str(e)}}
            return

        if isinstance(res, dict):
            output = res.get("output", "")
        else:
            output = str(res)

        # Simulate streaming by yielding the full output as a single chunk
        await asyncio.sleep(0)
        yield {"event": "on_chat_model_stream", "data": {"chunk": SimpleNamespace(content=output)}}
