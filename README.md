# EcoToxFred - Dialogues with a Knowledge Keeper

This is EcoToxFred, a Neo4j-backed Chatbot with whom you can discuss environmental monitoring data collected in a large knowledge graph and stored in a Neo4j Graph Database.

**EcoToxFred is a prototype** that demonstrates how domain-specific knowledge can be combined with LLMs to 
facilitate the interaction between users and (domain-specific) knowledge.

<p><img align="left" width="100" src="figures/assistant.png" />
EcoToxFred can answer questions about chemicals and their measured concentrations in European surface waters like rivers and lakes.
EcoToxFred is a friendly and intuitive chatbot designed to help researchers, stakeholders, and users explore and analyze chemical concentrations and toxicity data in European surface waters.
By leveraging advanced language models and a graph database, EcoToxFred makes complex environmental toxicology data 
accessible and understandable for everyone, regardless of their technical background.
</p>

<p align="center"><img width="400" src="figures/show_tool.png" /></p>

In its currently trained state, it can

- provide general information about rivers, lakes, or substances
- provide sampling sites where individual (sets of) chemicals have been measured and detected at which concentrations
- plot measured concentrations across time and/or sampling sites
- find all substances measured at a certain sampling site (identified by country, water body, or coordinate range)
- identify the most frequent drivers in regions (countries, water bodies, Europe)
- extract summarized risk for regions or species

Upcoming skills are

- plot requested information on a map of the selected region
- provide subgraphs of graph database results, ready to be used in Cytoscape or else

## Running the application

To run the application, you must install the libraries listed in `requirements.txt`.

```{sh}
pip install -r requirements.txt
```

Then run the `streamlit run` command to start the app on [localhost:8501](http://localhost:8501/).

```{sh}
streamlit run bot.py
```

### Quick-Start with Docker

If you prefer to use Docker, you just can run the app including the Neo4j-Database with:

```shell
docker compose up --renew-anon-volumes --build
```

## Contributing

You may experience that *EcoToxFred* does not provide appropriate responses.
Please provide your query and your expected response, and we will improve LLM prompts,
provide more examples for zero-shot and few-shot learning,
and if necessary even make improvements or adjustments to our Neo4j database
(e.g., by integrating additional knowledge).

## Contact

Jana Schor - jana.schor@ufz.de
