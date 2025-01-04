"""Tool for the Wikipedia API."""

from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


class WikipediaToolInput(BaseModel):
    """Input for the WikipediaQuery tool."""

    query: str = Field(
        description=(
            "A concise search query related to a chemical substance, its properties, "
            "environmental behavior, toxicity, or relevance to aquatic ecosystems. "
            "The query should be specific enough to retrieve relevant Wikipedia information."
        )
    )


class WikipediaTool(BaseTool):
    """Tool that searches the Wikipedia API for chemical and environmental toxicology-related information."""

    name: str = "Wikipedia"
    description: str = (
        "A specialized wrapper around Wikipedia for retrieving detailed information about chemicals, their properties, "
        "uses, environmental behavior, and toxicity. "
        "Useful for answering questions about chemical substances relevant to environmental monitoring, their potential "
        "toxicity to aquatic species (e.g., algae, daphnia/crustaceans, and fish), and their environmental impact. "
        "Input should be a search query related to a chemical or its associated properties."
    )
    api_wrapper: WikipediaAPIWrapper = Field(default_factory=WikipediaAPIWrapper)

    args_schema: Type[BaseModel] = WikipediaToolInput


    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Wikipedia tool."""
        return self.api_wrapper.run(query)
