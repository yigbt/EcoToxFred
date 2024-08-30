from langchain_core.output_parsers import StrOutputParser

from llm import llm, get_chat_llm
from graph import graph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

decider_prompt = """Given the user question and the cypher query that was used to extract data from the graph database, 
classify the question either as
 - `Text` if the user expects an answer in text form
 - `Plot` if the user expects a plot
 - `Map` if the users expects an image of a map with annotated sites

Do not respond with more than one word.

<question>
{question}
</question>

<cypher>
{cypher}
<cypher>

Classification:"""


decider_chain = (
        PromptTemplate.from_template(decider_prompt)
        | get_chat_llm()
        | StrOutputParser()
)

# TODO: Implement routing and single chains for text answers, plotting and maps.
# text_answer_chain = PromptTemplate.from_template(
# """You are an expert in langchain. \
# Always answer questions starting with "As Harrison Chase told me". \
# Respond to the following question:
#
# Question: {question}
# Answer:"""
# ) | ChatAnthropic(model_name="claude-3-haiku-20240307")
#
#
# def router(info):
#     if "text" in info["topic"].lower():
#         return text_answer_chain
#     elif "plot" in info["topic"].lower():
#         return langchain_chain
#     elif "map" in info["topic"].lower():
#         return langchain_chain
#     else:
#         return general_chain

def create_cypher_qa_chain(prompt_template: PromptTemplate) -> GraphCypherQAChain:
    """
    Creates a GraphCypherQAChain using the provided prompt template and Neo4j graph.

    Args:
        prompt_template (PromptTemplate): The prompt template for Cypher queries
    """
    chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=prompt_template,
        return_intermediate_steps=True,
    )
    chain.return_direct = True
    return chain
