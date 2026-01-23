from llm import get_chat_llm
from prompts import Prompts
from dotenv import load_dotenv
from tools.geographic_map import GeographicMap
from tools.wikipedia import WikipediaSearch
from tools.cypher import CypherSearch
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
import asyncio
from langchain_core.runnables import RunnableConfig

load_dotenv()

class UpdatedEcoToxFredAgent:


    def __init__(self):
        self.pm_tool = GeographicMap()
        self.wiki_tool = WikipediaSearch()
        self.cypher_tool = CypherSearch()
        self.tools = [self.pm_tool, self.cypher_tool, self.wiki_tool]
        self.llm = get_chat_llm()
        self.agent = create_agent(model=self.llm,
                                  tools=self.tools,
                                  system_prompt=Prompts.agent.prompt,
                                  middleware=[TodoListMiddleware()])

    def astream_events(self, messages):
        return self.agent.astream_events(messages, config=RunnableConfig(recursion_limit=50),version="v2")

if __name__ == "__main__":
    agent = UpdatedEcoToxFredAgent()

    async def main():
        current_node = ""
        async for event in agent.astream_events(
            {"messages": "What is your expertise?"}
        ):
            kind = event["event"]

            if kind == "on_tool_start":
                print("\n🔧 TOOL START")
                print("Name:", event["name"])
                print("Input:", event["data"].get("input"))

            elif kind == "on_tool_end":
                print("\n✅ TOOL END")
                print("Name:", event["name"])
                print("Output:", event["data"].get("output"))

            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    print(chunk)
                    print(event["metadata"]["langgraph_node"])

    asyncio.run(main())
