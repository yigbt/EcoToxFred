from typing import Any

from langchain_core.tools import BaseTool

from tools import cypher_utils


class PlotMap(BaseTool):
    cypher_chain = cypher_utils.create_direct_cypher_chain(prompt_template=create_cypher_prompt_template())

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass
