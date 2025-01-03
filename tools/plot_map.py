from logging import getLogger
from typing import Any, Type, Optional, Dict

import pandas as pd
import plotly.express as px
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field, model_validator

from graph import connect_to_neo4j
from llm import get_chat_llm
from prompts import Prompts, get_graph_meta_data

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
        results = self.cypher_chain.invoke({"query": query})
        df_description = "NO DATA WAS FOUND"
        artifact = None
        if "result" in results and len(results["result"]) > 0:
            df = pd.DataFrame(results["result"])
            df_description = df.describe(include='all').to_json()
            artifact = PlotMap.create_plotly_map(results["result"])
        answer = f"""
            A map with annotated sites is shown to the user.
            You receive the summarized statistics of the data that is shown on the map.
            Create a compelling figure caption from the summarized statistics.
            You MUST only provide the figure caption.
            
            <summary>
            {df_description}
            </summary>
            """

        return {"content": answer, "artifact": artifact}

    @staticmethod
    def create_plotly_map(result) -> Any:
        df = pd.DataFrame(result)

        # Check if dataframe has keys SiteName, Lat, and Lon
        required_columns = ["SiteName", "Lat", "Lon", "ChemicalName"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ToolException(f"Returned database result is missing the required columns: {missing_columns}")

        value_columns = ["Concentration", "DriverImportance", "ratioTU", "sumTU", "maxTU"]
        selected_target_column = None
        for v in value_columns:
            if v in df.columns:
                selected_target_column = v
                break

        if selected_target_column is not None:
            # Group by 'SiteName', 'Lat', 'Lon' and sum the 'Concentration'
            result_df = df.groupby(['SiteName', 'Lat', 'Lon']).agg({
                selected_target_column: 'median',
                'ChemicalName': 'first'  # Keep the first non-null value of ChemicalName
            }).reset_index()
            return PlotMap.render_concentration_map(result_df, {"target_column": selected_target_column})
        else:
            result_df = df[['SiteName', 'Lat', 'Lon', "ChemicalName"]].drop_duplicates()
            result_df["Occurrence"] = 1
            return PlotMap.render_occurrence_map(result_df, {})

    @staticmethod
    def render_concentration_map(df: pd.DataFrame, meta_info: dict) -> Any:
        fig = px.scatter_geo(
            df,
            lat="Lat",
            lon="Lon",
            hover_name="SiteName",
            size=meta_info["target_column"],
            color=meta_info["target_column"],
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

    @staticmethod
    def render_occurrence_map(df: pd.DataFrame, meta_info: dict) -> Any:
        fig = px.scatter_geo(
            df,
            lat="Lat",
            lon="Lon",
            hover_name="SiteName",
            # TODO: Jana, fix what you want here
            # size=0.25,
            # color="Occurrence"
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
    query: str = Field(
        description="Human readable question that asks about chemical substances and where or when they have been measured in European surface water.")


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
