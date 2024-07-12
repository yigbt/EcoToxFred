from llm import llm
from graph import graph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
import networkx as nx
import matplotlib.pyplot as plt


def create_cypher_prompt_template():
    """
    Creates a prompt template for Cypher queries.

    Returns:
        PromptTemplate: The Cypher prompt template
    """
    return PromptTemplate.from_template("""
        You are an expert Neo4j Developer translating user questions into Cypher to answer questions about chemicals, 
        and their measured concentrations in European surface waters like rivers and lakes. 
        Convert the user's question based on the schema.
        
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        
        Do return entire nodes and relations in JSON format.
        
        Schema:
        {schema}
        
        Context:
        Chemicals are substances.
        The chemical name is stored in the name property of the Substance nodes. 
        The sampling site's name is stored in the name property of the Site nodes.
        Chemical concentrations are stored as mean_concentration and median_concentrations, which are the quarterly 
        summarized concentrations of multiple measurements. 
        Rivers and lakes are water bodies and larger areas around rivers and lake including smaller streams are 
        collected in river basins.
        The DTXSID referes to the CompTox Dashboard ID of the U.S. EPA.
        The verb detected in the context of chemical monitoring referes to a measured concentration above 0.
        
        Instructions:
        Ignore water_body and country in case you are only asked about finding information on a certain chemical.
        If you cannot find the requested chemical name, ask the user to provide the Comptox Dashboard ID of the 
        requested chemical which is the DTXSID.
        For questions that involve time or the interrogative 'when' refer to the node and relation properties year 
        and quarter.
        If you cannot find the requested river name in water_body search in river_basin and vice versa.
        For questions that involve geographic or location information or the interrogative 'where' search in the 
        properties of the Site nodes.
        For questions that involve toxicity information use the toxic unit properties 'TU' or 'sumTU' of the relations
        measured_at and summarized_impact_on.
        In case the result contains multiple values, return introductory sentences followed by a list of the values.
    
        
        Example Cypher Queries:
        0. To find information about a certain substance
        ```
        MATCH (s:Substance) 
        WHERE s.name = 'Diuron'
        return s
        ```
        1. To find sites where a certain substance has been measured
        ```
        MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
        WHERE s.name='Diuron'
        RETURN s, r, l
        ```
        
        2. To find sites where a certain substance has been measured with a mean concentration above a threshold:
        ```
        MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site)
        WHERE s.name='Diuron' AND r.mean_concentration > 0.001
        RETURN s, r, l
        ```
        
        3. To find all chemicals measured in a certain river:
        ```
        MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site)
        WHERE s.water_body = 'seine' AND r.mean_concentration > 0.001
        RETURN c, r, s
        ```
        
        4. To find all substances measured in France
        ```
        MATCH (c:Substance)-[r:MEASURED_AT]->(s:Site)
        WHERE s.country = 'France'
        RETURN DISTINCT c, r, s
        ```
        
        5. To find the most frequent driver chemicals 
        ```
        MATCH (s:Substance)-[r:IS_DRIVER]->(l:Site)
        WHERE r.driver_importance > 0.8
        RETURN DISTINCT s, r, l
        ```
        Question:
        {question}
        
        Cypher Query:""")


def create_cypher_qa_chain(prompt_template: PromptTemplate) -> GraphCypherQAChain:
    """
    Creates a GraphCypherQAChain using the provided prompt template and Neo4j graph.

    Args:
        prompt_template (PromptTemplate): The prompt template for Cypher queries
    """
    return GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=prompt_template,
        return_intermediate_steps=True,
    )


def visualize_graph(graph_to_plot: nx.Graph):
    pos = nx.spring_layout(graph_to_plot)
    plt.figure(figsize=(12, 8))
    nx.draw(graph_to_plot, pos, with_labels=True, node_color='skyblue',
            edge_color='gray')  # , node_size=2000, font_size=15)
    plt.savefig('/home/hertelj/git-hertelj/llm-chatbot-python/figures/result_graph.png')
    # plt.show()


cypher_qa = create_cypher_qa_chain(prompt_template=create_cypher_prompt_template())
result = cypher_qa.invoke({"query": "Return the Cypher query for the question to provide the DTXSID of Diuron"})
cypher_query = result['intermediate_steps'][0]['query']
cypher_query = "MATCH (s:Substance)-[r:MEASURED_AT]->(l:Site) WHERE s.name = 'Diuron' AND r.mean_concentration > 0.005 RETURN s,r,l"
graph_db_result = graph.query(query=cypher_query)
# transform to nodes, edges
result_graph = nx.Graph()
for record in graph_db_result:
    if 's' in record.keys():
        result_graph.add_node(record['s']['DTXSID'], label='Substance', **record['s'])
    elif 'r' in record.keys():
        pass
    elif 'l' in record.keys():
        result_graph.add_node(record['l']['name'], label='Site', **record['l'])

visualize_graph(graph_to_plot=result_graph)