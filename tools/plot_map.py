from typing import Any, Type, Optional

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field

import pandas as pd
import plotly.express as px

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts

# TODO: Most of this is boilerplate for now. Need to fix prompt first
class PlotMapInput(BaseModel):
    query: str = Field(description="Search query that is turned into a Cypher query for a graph database")

class PlotMap(BaseTool):
    name = "Geographic Map"
    description = ("Use this tool to plot geographic locations on a map when the user's query involves the location of "
                   "chemicals, their concentrations, or any geographical distribution data in European surface waters, "
                   "such as rivers and lakes.")
    args_schema: Type[BaseModel] = PlotMapInput
    response_format: str = "content_and_artifact"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        self.max_results = 100
        self.prompt = Prompts.cypher_map
        self.llm = get_chat_llm()
        self.graph = connect_to_neo4j()
        self.cypher_chain = GraphCypherQAChain.from_llm(
            self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=self.prompt.get_prompt_template(),
            return_intermediate_steps=True,
        )
        self.cypher_chain.return_direct = True
        self.cypher_chain.top_k = self.max_results

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        results = self.cypher_chain.invoke({"query": query})
        # Check validity of result and create Pandas df from it
        df = PlotMap.create_pandas_from_result(results)
        rendered_image = PlotMap.render_image(df)

        response = "Call LLM to get a description of the image?"
        return response, rendered_image

    @staticmethod
    def create_pandas_from_result(result) -> pd.DataFrame:
        return pd.DataFrame.from_dict({})

    @staticmethod
    def render_image(data: Any) -> Any:
        # TODO: fix what type data is supposed to be.
        df = pd.DataFrame.from_dict(data)
        df["sumTU"] = df["tu"].astype(float)
        fig = px.scatter_geo(
            df,
            lat=df.lat,
            lon=df.lon,
            hover_name="name",
            size="sumTU"
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
