from logging import getLogger
from typing import Any, Type, Optional, Dict

import pandas as pd
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field, model_validator

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts
from tools.plotly_visualization import create_plotly_map

logger = getLogger(__name__)

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

    cypher_chain: Any

    def run(self, query: str) -> dict:
        results = self.cypher_chain.invoke({"query": query})
        df_description = "NO DATA WAS FOUND"
        artifact = None
        if "result" in results and len(results["result"]) > 0:
            df = pd.DataFrame(results["result"])
            df_description = df.describe(include='all').to_json()
            try:
                artifact = create_plotly_map(results["result"])
            except Exception as e:
                raise ToolException(f"Error creating plotly map: {e}")
        answer = f"""
            A map with annotated sites is shown to the user.
            You receive the summarized statistics of the data that is shown on the map.
            Create a compelling figure caption from the summarized statistics.
            
            <summary>
            {df_description}
            </summary>
            """

        return {"content": answer, "artifact": artifact}


class PlotMapInput(BaseModel):
    query: str = Field(
        description="Human readable question that asks about where a specific substance (e.g., Atrazine) has been "
                    "measured or detected, optionally at a certain time frame (e.g., in the year 2011) and/or with "
                    "toxicity information for a certain species (e.g., algae) to generate a map showing relevant "
                    "sampling sites and data either for entire Europe or a provided lake, river, or country.")


class PlotMapTool(BaseTool):
    name: str = "GeographicMap"
    description: str = ("This tool fetches chemicals' location and measurements in European surface waters "
                        "from a graph database and plots geographic locations on a map. "
                        "The input must be a complete sentence requesting sites. "
                        "Example inputs: \n\n"
                        "Show sites where Diuron has been measured on the European map.\n"
                        "Show Diuron's measured concentrations on the European map.\n"
                        "Show Diuron's toxic unit (TU) distribution since 2010 for the species algae (unicellular).\n"
                        "Show Diuron's driver importance distribution in France between January 2010 and December 2012.")
    args_schema: Type[BaseModel] = PlotMapInput
    response_format: str = "content_and_artifact"
    plot_map: PlotMap = Field(default_factory=PlotMap)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        result = self.plot_map.run(query)
        return result["content"], result["artifact"]
