import pytest

from prompts import CypherExampleCollections
from typing import List
from utils import connect_to_neo4j_for_test


@pytest.fixture(scope="session")
def database_connection():
    try:
        db = connect_to_neo4j_for_test()
        assert db is not None
        yield db
    except:
        assert False, "No database connection could be established"


# For now, simply combining all available Cypher examples and running all of them.
cypher_examples: List[dict] = (CypherExampleCollections.general_cypher_queries.examples +
                               CypherExampleCollections.map_cypher_queries.examples)


@pytest.mark.parametrize("example", cypher_examples, ids=[e["information"][:40] for e in cypher_examples])
def test_cypher_query(database_connection, example):
    try:
        assert "cypher" in example.keys()
        database_connection.query(example["cypher"])
    except ValueError as e:
        assert False, f"Invalid cypher query: {e}"


def test_example_for_vizualization(database_connection):
    cypher_example = """
        MATCH (l:Site)-[r:SUMMARIZED_IMPACT_ON]->(s:Species)
        WHERE s.name = 'algae' AND r.year >= 2010
        RETURN s.name AS SpeciesName, // plot title
        r.sumTU AS sumTU, // >=0, continuous point color from yellow to red, with midpoint orange at 0.001
        r.year AS Year, r.quarter AS Quarter, // add to point hover
        l.name AS SiteName, // point hover
        l.water_body AS WaterBody, l.river_basin AS RiverBasin, // point hover
        l.lat AS Lat, l.lon AS Lon // x,y coordinates
        ORDER BY r.sumTU DESC
    """
    try:
        import pandas as pd
        from tools.plotly_visualization import create_plotly_map
        result = database_connection.query(cypher_example)
        df = pd.DataFrame(result)
        fig = create_plotly_map(df)
        print(fig)
    except ValueError as e:
        assert False, f"Invalid cypher query: {e}"