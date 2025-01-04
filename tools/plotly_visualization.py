import plotly.express as px
import pandas as pd
from typing import Any

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

def create_plotly_map(result) -> Any:
    df = pd.DataFrame(result)

    # Check if dataframe has keys SiteName, Lat, and Lon
    required_columns = ["SiteName", "Lat", "Lon", "ChemicalName"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Returned database result is missing the required columns: {missing_columns}")

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
        return render_concentration_map(result_df, {"target_column": selected_target_column})
    else:
        result_df = df[['SiteName', 'Lat', 'Lon', "ChemicalName"]].drop_duplicates()
        result_df["Occurrence"] = 1
        return render_occurrence_map(result_df, {})

