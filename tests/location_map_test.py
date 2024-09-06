from graph import graph
import pandas as pd
import plotly.express as px

locations_cypher = \
    """MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
    WHERE r.year > 2010
    RETURN l.name as name, l.lat as lat, l.lon as lon, r.sumTU as tu LIMIT 25
    """


def test_location_map():
    result = graph.query(locations_cypher)
    df = pd.DataFrame.from_dict(result)
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
