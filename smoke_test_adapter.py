import asyncio
import json
from adapters.agent_executor_shim import AgentExecutorShim

async def test_stream_and_calls():
    print("Creating AgentExecutorShim...")
    a = AgentExecutorShim(model="gpt-4", tools=[])

    # Test run (sync)
    try:
        out = a.run("Hello world from run()")
        print("run() output:", out)
    except Exception as e:
        print("run() raised:", repr(e))

    # Test invoke (dict)
    try:
        res = a.invoke({"input": "Hello from invoke()"})
        print("invoke() output:", json.dumps(res))
    except Exception as e:
        print("invoke() raised:", repr(e))

    # Test __call__
    try:
        call_res = a("Hello from __call__")
        print("__call__ output:", call_res)
    except Exception as e:
        print("__call__ raised:", repr(e))

    # Test streaming async events
    print("Testing astream_events...")
    try:
        async for ev in a.astream_events({"input": "Stream: Final Answer: 42"}):
            print("STREAM EVENT:", ev)
    except Exception as e:
        print("astream_events raised:", repr(e))

if __name__ == "__main__":
    asyncio.run(test_stream_and_calls())
