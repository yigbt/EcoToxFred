from langchain_neo4j import Neo4jGraph
import streamlit as st


def connect_to_neo4j() -> Neo4jGraph:
    """
    Connects to a Neo4j graph using the provided credentials.

    Returns:
        Neo4jGraph: The Neo4j graph instance
    """
    # TODO: Catch ValueError("Cannot resolve address {}".format(address))
    # ValueError: Could not connect to Neo4j database. Please ensure that the url is correct
    return Neo4jGraph(
        url=st.secrets["NEO4J_URI"],
        username=st.secrets["NEO4J_USERNAME"],
        password=st.secrets["NEO4J_PASSWORD"]
    )

# Connect to Neo4j and provide the graph as
# from graph import graph
graph = connect_to_neo4j()
