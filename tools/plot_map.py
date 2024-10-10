from typing import Any, Type, Optional, Dict

import pandas as pd
import plotly.express as px
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_community.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, model_validator
# from pydantic.v1 import BaseModel, Field, root_validator

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts, get_graph_meta_data, Prompt
from logging import getLogger

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
        values["prompt"] = Prompts.cypher_map
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
        results = self.cypher_chain.invoke({"query": query, "meta": get_graph_meta_data()})
        # # Check validity of result and create Pandas df from it
        df = PlotMap.create_pandas_from_result(results["result"])
        rendered_image = PlotMap.render_image(df)
        return {"figure": rendered_image}

    @staticmethod
    def create_pandas_from_result(result) -> pd.DataFrame:
        df = pd.DataFrame(result)

        # Group by 'SiteName', 'Lat', 'Lon' and sum the 'Concentration'
        result_df = df.groupby(['SiteName', 'Lat', 'Lon']).agg({
            'Concentration': 'sum',
            'ChemicalName': 'first'  # Keep the first non-null value of ChemicalName
        }).reset_index()

        return result_df

    @staticmethod
    def render_image(df: pd.DataFrame) -> Any:
        fig = px.scatter_geo(
            df,
            lat="Lat",
            lon="Lon",
            hover_name="SiteName",
            size="Concentration",
            color="Concentration",
            color_continuous_scale=px.colors.sequential.YlOrRd
        )

        fig.update_layout(
            geo=dict(
                scope='europe',
                showland=True,
                landcolor="rgb(212, 212, 212)",
                subunitcolor="rgb(255, 255, 255)",
                countrycolor="rgb(255, 255, 255)",
                showlakes=True,
                showrivers=True,
                lakecolor="rgb(135, 206, 235)",
                rivercolor="rgb(135, 206, 235)",
                showsubunits=True,
                showcountries=True,
                resolution=50,
                lonaxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    dtick=5
                ),
                lataxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    dtick=5
                )
            )
        )
        return fig


# TODO: Most of this is boilerplate for now. Need to fix prompt first
class PlotMapInput(BaseModel):
    query: str = Field(description="Search query that is turned into a Cypher query for a graph database")


class PlotMapTool(BaseTool):
    name: str = "Geographic Map"
    description: str = ("This tool fetches chemicals' location and measurements in European surface waters "
                        "from a graph database and plots geographic locations on a map. "
                        "The input must be a complete sentence requesting sites. "
                        "Example inputs: \n\n"
                        "Show Diuron's measured concentrations on the European map.\n"
                        "Show Diuron's toxic unit (TU) distribution since 2010 for the species algae (unicellular).\n"
                        "Show Diuron's driver importance distribution in France between January 2010 and December 2012.")
    args_schema: Type[BaseModel] = PlotMapInput
    response_format: str = "content_and_artifact"
    plot_map: PlotMap = Field(default_factory=PlotMap)

    def run_with_args(self, query: str) -> Any:
        from uuid import uuid4
        tool_call_id = f"plot_map_{uuid4().hex}"
        return self.invoke({
            "args": {"query": query},
            "id": tool_call_id,
            "type": "tool_call"}
        )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        figure = self.plot_map.run(query)
        contents = "A map with annotated sites."
        return contents, figure["figure"]
        # logger.info(f"QUERY: \n\n{query}\n\n")
        # return query, "Test"
