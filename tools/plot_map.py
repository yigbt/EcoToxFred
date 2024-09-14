from typing import Any, Type, Optional, Dict

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field, root_validator

import pandas as pd
import plotly.express as px

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts, get_graph_meta_data, Prompt

class PlotMap(BaseModel):
    prompt: Any
    chat_llm: Any
    graph: Any
    cypher_chain: Any

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        values["chat_llm"] = get_chat_llm()
        values["prompt"] = Prompts.cypher_map
        values["graph"] = connect_to_neo4j()
        values["cypher_chain"] = GraphCypherQAChain.from_llm(
            values["chat_llm"],
            graph=values["graph"],
            verbose=True,
            cypher_prompt=values["prompt"].get_prompt_template(),
            return_intermediate_steps=True,
        )
        values["cypher_chain"].return_direct = True
        values["cypher_chain"].top_k = 100
        return values

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
            lat=df.Lat,
            lon=df.Lon,
            hover_name="SiteName",
            size="Concentration",
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
                lakecolor="rgb(0, 20, 100)",
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
    question: str = Field(description="Search query that is turned into a Cypher query for a graph database")

class PlotMapTool(BaseTool):
    name = "Geographic Map"
    description = ("Use this tool to plot geographic locations on a map when the user's query involves the location of "
                   "chemicals, their concentrations, or any geographical distribution data in European surface waters, "
                   "such as rivers and lakes.")
    args_schema: Type[BaseModel] = PlotMapInput
    response_format: str = "content"

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        results = self.cypher_chain.invoke({"question": query, "meta": get_graph_meta_data()})
        # # Check validity of result and create Pandas df from it
        # df = PlotMap.create_pandas_from_result(results)
        # rendered_image = PlotMap.render_image(df)
        #
        response = "Call LLM to get a description of the image?"
        return response
