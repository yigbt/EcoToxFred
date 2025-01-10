from typing import Any, Type, Optional, Dict

import pandas as pd
import plotly.io
from langchain_neo4j import GraphCypherQAChain
from langchain_community.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field, model_validator

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts, ToolDescriptions
from tools.plotly_visualization import create_plotly_map

class PlotMap(BaseModel):
    prompt: Any
    chat_llm: Any
    graph: Any
    cypher_chain: Any

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        values["chat_llm"] = get_chat_llm()
        values["prompt"] = Prompts.geographic_map
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
        values["cypher_chain"].top_k = 10000
        return values

    def run(self, query: str) -> dict:
        results = self.cypher_chain.invoke({"query": query})
        df_description = "NO DATA WAS FOUND"

        # We store the generated Cypher query and return it in the tool's exception in
        # case we did not receive the data we needed. The agent might be able to understand
        # the missing pieces, refine the question and run the tool again.
        generated_cypher = results["intermediate_steps"][-1]["query"]
        if "result" in results and len(results["result"]) > 0:
            df = pd.DataFrame(results["result"])
            df_description = df.describe(include='all').to_json(default_handler=str)
            try:
                artifact = create_plotly_map(results["result"])
            except Exception as e:
                raise ToolException(f"Could not create plotly from data from the following cypher: {generated_cypher}"
                                    f"The plotly error was: {e}")
        else:
            raise ToolException(f"No data was found for the following cypher: {generated_cypher}")
        answer = f"""
            A map with annotated sites is shown to the user.
            You receive the summarized statistics of the data that is shown on the map.
            Create a compelling figure caption from the summarized statistics.
            
            <summary>
            {df_description}
            </summary>
            """

        return {"content": answer, "artifact": artifact}


class GeographicMapInput(BaseModel):
    query: str = Field(description=ToolDescriptions.get("GeographicMapInput", "query"))


class GeographicMap(BaseTool):
    name: str = "GeographicMap"
    description: str = ToolDescriptions.get("GeographicMap", "description")
    args_schema: Type[BaseModel] = GeographicMapInput
    response_format: str = "content_and_artifact"
    plot_map: PlotMap = Field(default_factory=PlotMap)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        result = self.plot_map.run(query)
        return result["content"], plotly.io.to_json(result["artifact"])
