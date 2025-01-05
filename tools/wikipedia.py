"""Tool for the Wikipedia API."""

from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

from prompts import (ToolDescriptions)


class WikipediaSearchInput(BaseModel):
    """Input for the WikipediaQuery tool."""

    query: str = Field(
        description=ToolDescriptions.get("WikipediaSearchInput", "query")
    )


class WikipediaSearch(BaseTool):
    """Tool that searches the Wikipedia API for chemical and environmental toxicology-related information."""

    name: str = ToolDescriptions.get("WikipediaSearch", "name")
    description: str = ToolDescriptions.get("WikipediaSearch", "description")
    api_wrapper: WikipediaAPIWrapper = Field(default_factory=WikipediaAPIWrapper)

    args_schema: Type[BaseModel] = WikipediaSearchInput


    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Wikipedia tool."""
        return self.api_wrapper.run(query)
