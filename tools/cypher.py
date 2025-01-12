from typing import Any, Type, Optional, Dict

import pandas as pd
from langchain_neo4j import GraphCypherQAChain
from langchain_community.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field, model_validator

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts, ToolDescriptions


class CypherSearchCore(BaseModel):
    prompt: Any
    chat_llm: Any
    graph: Any
    cypher_chain: Any

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        values["chat_llm"] = get_chat_llm()
        values["prompt"] = Prompts.cypher_search
        values["graph"] = connect_to_neo4j()
        values["cypher_chain"] = GraphCypherQAChain.from_llm(
            values["chat_llm"],
            graph=values["graph"],
            verbose=True,
            cypher_prompt=values["prompt"].get_prompt_template(),
            return_intermediate_steps=True,
            allow_dangerous_requests=True
        )
        values["cypher_chain"].return_direct = True
        values["cypher_chain"].top_k = 1000
        return values

    def run(self, query: str) -> str:
        results = self.cypher_chain.invoke({"query": query})
        max_results_shown = 5
        results_cropped = False

        # We store the generated Cypher query and return it in the tool's exception in
        # case we did not receive the data we needed. The agent might be able to understand
        # the missing pieces, refine the question and run the tool again.
        generated_cypher = results["intermediate_steps"][-1]["query"]
        if "result" in results and len(results["result"]) > 0:
            df = pd.DataFrame(results["result"])
            df_description = df.describe(include='all').to_json(default_handler=str)
            if df.shape[0] > max_results_shown:
                df = df[:max_results_shown]
                results_cropped = True
            df_json = df.to_json(default_handler=str)

        else:
            raise ToolException(f"No data was found for the following cypher: {generated_cypher}")

        cropping_message = ""
        if results_cropped:
            cropping_message = f"""
            The full results cropped to {max_results_shown} rows:
            """
        else:
            cropping_message = f"""
            The results comprise {df.shape[0]} rows:
            """

        answer = f"""
            {cropping_message}
            <data>
            {df_json}
            </data>
            
            Provide the user with a Markdown formatted table of the data and a textual summary.
            <summary>
            {df_description}
            </summary>
            
            Always provide the following cypher query as code to the user
            ``` 
            {generated_cypher}
            ```
            
            Always provide the Zenodo link `https://zenodo.org/records/14616124` of the docker container holding
            the full Neo4j graph database where the user can access the complete result with the cypher query.
            """

        return answer


class CypherSearchInput(BaseModel):
    query: str = Field(description=ToolDescriptions.get("CypherSearchInput", "query"))


class CypherSearch(BaseTool):
    name: str = "CypherSearch"
    description: str = ToolDescriptions.get("CypherSearch", "description")
    args_schema: Type[BaseModel] = CypherSearchInput
    response_format: str = "content"
    search_core: CypherSearchCore = Field(default_factory=CypherSearchCore)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        result = self.search_core.run(query)
        return result
