import plotly.express as px
import pandas as pd
from typing import Any


def render_concentration_map(df: pd.DataFrame, meta_info: dict) -> Any:
    target_color = {
        "tu": px.colors.sequential.Bluered,
        "sumtu": px.colors.sequential.Bluered,
        "maxtu": px.colors.sequential.Bluered,
        "ratiotu": px.colors.sequential.Plasma,
        "driverimportance": px.colors.sequential.Reds,
        "concentration": ["blue", "darkred"]
    }
    target_midpoint = {
        "tu": 0.5,
        "sumtu": 0.001,
        "maxtu": 0.001,
        "ratiotu": 0.5,
        "driverimportance": 0.5,
        "concentration": None

    }
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="sitename",
        hover_data=df[meta_info["meta_data_columns"]],
        size=meta_info["target_column"],
        color=meta_info["target_column"],
        color_continuous_scale=target_color[meta_info["target_column"]],
        color_continuous_midpoint=target_midpoint[meta_info["target_column"]]
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
        lat="lat",
        lon="lon",
        hover_name="sitename",
        hover_data=df[meta_info["meta_data_columns"]],
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
    # Check if dataframe has keys sitename, Lat, and Lon
    df.columns = df.columns.str.lower()

    required_columns = ["sitename", "lat", "lon"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Returned database result is missing the required columns: {missing_columns}")

    value_columns = ["concentration", "driverimportance", "tu", "ratiotu", "sumtu", "maxtu"]
    selected_target_column = None
    for v in value_columns:
        if v in df.columns:
            selected_target_column = v
            break

    optional_meta_data_columns = ["waterbody", "riverbasin", "country", "year", "quarter"]
    meta_data_columns = [col for col in optional_meta_data_columns if col in df.columns]
    if selected_target_column is not None:
        if selected_target_column in ['sumtu', 'ratiotu', 'maxtu']:
            # Group by 'sitename', 'Lat', 'Lon' and average the aggregated TU for each site
            result_df = df.groupby(['sitename', 'lat', 'lon'] + meta_data_columns).agg({
                selected_target_column: 'median'
            }).reset_index()
        else:
            # Group by 'sitename', 'Lat', 'Lon' and average the concentration for each substance
            result_df = df.groupby(['sitename', 'lat', 'lon'] + meta_data_columns).agg({
                selected_target_column: 'median',
                'chemicalname': 'first'  # Keep the first non-null value of ChemicalName
            }).reset_index()
        return render_concentration_map(result_df,
                                        {"target_column": selected_target_column,
                                         "meta_data_columns": meta_data_columns})
    else:
        result_df = df[['sitename', 'lat', 'lon', "chemicalname"] + meta_data_columns].drop_duplicates()
        #result_df["Occurrence"] = 1
        return render_occurrence_map(result_df, {"meta_data_columns": meta_data_columns})
