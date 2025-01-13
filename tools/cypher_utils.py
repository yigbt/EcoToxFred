from llm import llm
from graph import graph
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

def create_direct_cypher_chain(
        prompt_template: PromptTemplate,
        number_max_results: int = 10) -> GraphCypherQAChain:
    """
    Creates a GraphCypherQAChain using the provided prompt template and Neo4j graph.

    Args:
        prompt_template (PromptTemplate): The prompt template for Cypher queries
        number_max_results (int): Maximum number of elements returned from the database query
    """
    chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=prompt_template,
        return_intermediate_steps=True,
        allow_dangerous_requests=True
    )
    chain.return_direct = True
    chain.top_k = number_max_results
    return chain
