import asyncio

import pytest
from ragas.metrics.collections import AgentGoalAccuracyWithoutReference,AgentGoalAccuracyWithReference, ToolCallAccuracy
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.messages import ToolCall, HumanMessage, AIMessage, ToolMessage
from agent import EcoToxFred
from typing import List
import langchain_core.messages as m
from forked_convert_langchain_to_ragas import convert_to_ragas_messages
from config import config
import json
ragas = pytest.importorskip("ragas")



async def _invoke_agent_async(question):
    """Invoke the agent in a worker thread and return its result.

    Args:
        question (str): User question to send to the agent.

    Returns:
        dict: Agent response payload, including messages.
    """
    agent = EcoToxFred()
    return await asyncio.to_thread(agent.invoke, {"messages": [m.HumanMessage(content=question)]})


async def evaluate(ragas_messages:List[HumanMessage | AIMessage | ToolMessage], config, reference_tool_calls=None, reference_answer=""):
    """Evaluate tool-call accuracy and goal accuracy for the given messages.

    Args:
        ragas_messages (list[dict]): Messages formatted for RAGAS evaluation.
        config (dict): Loaded configuration containing the OpenAI API key.
        reference_tool_calls (list[dict] | None): Optional tool call references.
        reference_answer (str): Optional reference answer for goal accuracy.

    Returns:
        tuple[float | None, float | None]: Tool-call score and goal score.
    """
    llm = llm_factory("gpt-4.1", client=AsyncOpenAI(api_key=config.get("OPENAI_API_KEY")))

    tool_result = None
    if reference_tool_calls:
        tool_metric = ToolCallAccuracy(strict_order=False)
        tool_result = await tool_metric.ascore(
            user_input=ragas_messages,
            reference_tool_calls=[ToolCall(name=call["name"], args=call["args"]) for call in reference_tool_calls],
        )
        print(ragas_messages)

    if reference_answer:
        goal_metric = AgentGoalAccuracyWithReference(llm=llm)
        goal_result = await goal_metric.ascore(
            user_input=ragas_messages,
            reference=reference_answer,
        )
    else:
        goal_metric = AgentGoalAccuracyWithoutReference(llm=llm)
        goal_result = await goal_metric.ascore(
            user_input=ragas_messages,
        )

    return (
        tool_result.value if tool_result is not None else None,
        goal_result.value if goal_result is not None else None,
    )


async def test_ragas_toolcall_accuracy_and_answer_correctness(dataset):
    """Run RAGAS evaluation for tool-call accuracy and goal correctness."""
    results = []

    for item in dataset:
        result = await _invoke_agent_async(item["question"])
        converted = convert_to_ragas_messages(result["messages"])

        tool_score, goal_score = await evaluate(
            converted,
            config,
            reference_tool_calls=item["tool_calls"],
            reference_answer=item["desired_outcome"],
        )
        if tool_score is not None:
            print(f"Tool Call Accuracy: {tool_score}")
        if goal_score is not None:
            print(f"Agent Goal Accuracy: {goal_score}")
        results.append((tool_score, goal_score))
    return results



if __name__ == "__main__":
    with open("test_set.json", "r") as f:
        dataset = json.load(f)["tests"]
    print(dataset)
    results = asyncio.run(test_ragas_toolcall_accuracy_and_answer_correctness(dataset))

