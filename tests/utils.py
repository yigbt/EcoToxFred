import os
import toml
from langchain_community.graphs import Neo4jGraph


def connect_to_neo4j_for_test() -> Neo4jGraph:
    current_file_path = os.path.abspath(__file__)
    file_directory = os.path.dirname(current_file_path)
    secrets_file = os.path.join(file_directory, os.pardir, '.streamlit', 'secrets.toml')
    with open(secrets_file) as f:
        secrets = toml.load(f)
    assert "NEO4J_URI" in secrets.keys()
    assert "NEO4J_USERNAME" in secrets.keys()
    assert "NEO4J_PASSWORD" in secrets.keys()
    return Neo4jGraph(
        url=secrets["NEO4J_URI"],
        username=secrets["NEO4J_USERNAME"],
        password=secrets["NEO4J_PASSWORD"]
    )
