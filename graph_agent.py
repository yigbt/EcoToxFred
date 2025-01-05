from langgraph.prebuilt.chat_agent_executor import create_react_agent

from llm import get_chat_llm
from tools.plot_map import GeographicMap
from tools.wikipedia import WikipediaSearch
from prompts import Prompts


class GraphEcoToxFredAgent:

    system_prompt = Prompts.agent.prompt

    def __init__(self):
        self.pm_tool = GeographicMap()
        self.wiki_tool = WikipediaSearch()
        self.tools = [self.pm_tool, self.wiki_tool]
        self.llm = get_chat_llm().bind_tools(self.tools, parallel_tool_calls=False)
        self.agent = create_react_agent(self.llm, self.tools)

    def invoke(self, messages):
        return self.agent.invoke(messages)

    def astream_events(self, messages):
        return self.agent.astream_events(messages, version="v2")