from langchain.smith import RunEvalConfig, run_on_dataset
from langchain_community.chat_models import ChatOpenAI
from langsmith import Client

# Import our new shim instead of LangChain’s ReAct agent
from adapters.agent_executor_shim import AgentExecutorShim


def agent_factory():
    """
    Factory that returns an XAgentAdapter (wrapped in our AgentExecutorShim).
    This replaces the old LangChain ReAct agent creation.
    """
    # Example LLM config (kept if you want to pass through model info)
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    # Define tools if needed (currently empty placeholder)
    tools = []

    # Create the shim-wrapped agent
    return AgentExecutorShim(llm=llm, tools=tools, prompt="You are XAgent inside L3AGI.")


# Instantiate agent
agent = agent_factory()

# LangSmith client for evaluation
client = Client()

# Define evaluation configuration
eval_config = RunEvalConfig(
    evaluators=[
        "qa",
        RunEvalConfig.Criteria("helpfulness"),
        RunEvalConfig.Criteria("conciseness"),
    ],
    input_key="input",
    eval_llm=ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo"),
)

# Run dataset evaluation using our XAgent-backed factory
chain_results = run_on_dataset(
    client,
    dataset_name="test-dataset",
    llm_or_chain_factory=agent_factory,
    evaluation=eval_config,
    concurrency_level=1,
    verbose=True,
)
