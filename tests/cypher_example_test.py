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
