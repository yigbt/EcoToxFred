from __future__ import annotations
import yaml
import os
import re
from typing import List

from sqlalchemy.util import classproperty

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
prompts_directory = os.path.join(current_directory, 'prompts')


class DefaultDict(dict):
    """Helper class to allow default values for a dictionary

    This is necessary to replace only some placeholders in an f-string.
    """

    def __missing__(self, key):
        return f"{{{key}}}"


class Prompt:
    """
    A Prompt is created from one specific YAML file that must have the following structure:

    parameters:
      - schema
      - examples
      - question
    prompt: |+
      Write your prompt here using newlines and the parameters like {schema} as you like.
    """
    def __init__(self, prompt_file: str):
        with open(prompt_file) as f:
            self.data = yaml.safe_load(f)
        self.prompt = self.data['prompt']
        if "parameters" in self.data.keys():
            self.parameters = set(self.data['parameters'])
        else:
            self.parameters = set()

    def append(self, other):
        self.prompt += "\n" + other.prompt
        self.parameters = self.parameters.union(other.parameters)

    def inject_examples(self, examples: CypherExampleCollection):
        assert len(examples.examples) > 0
        assert "examples" in self.parameters
        self.partial_apply({"examples": examples.format_examples_as_markdown()})

    def partial_apply(self, parameters: dict):
        params_key_set = set(parameters.keys())
        assert params_key_set.issubset(set(self.parameters))
        self.prompt = self.prompt.format_map(DefaultDict(parameters))
        self.parameters = set(self.parameters) - params_key_set


class Prompts:
    """
    Helper class to get easy access to all prompts.

    If you add another prompt YAML file, please add the appropriate classproperty here as well.
    Also, if we create partial prompts that we need to build up by merging them,
    this would be the right place for it.
    """
    @classproperty
    def general_cypher_prompt(self) -> Prompt:
        return Prompt(os.path.join(prompts_directory, "general_cypher_prompt.yml"))


class CypherExampleCollection:
    """
    CypherExampleCollection class for processing and organizing Cypher query examples from a specified file.

    It holds a number of example Cypher queries together with their corresponding descriptions.
    It can format these examples as a block of Markdown code to inject them into a prompt.
    """

    def __init__(self, example_file: str):
        self.examples: List[dict] = []
        self.read_cypher_file(example_file)

    def get_queries(self) -> List[str]:
        """Returns the list of Cypher queries for this collection."""
        return [e["cypher"] for e in self.examples]

    def format_examples_as_markdown(self) -> str:
        result_lines = []
        for i in range(len(self.examples)):
            result_lines.append(f"{i}. {self.examples[i]['information']}")
            result_lines.append("```cypher")
            result_lines.append(self.examples[i]['cypher'])
            if i < len(self.examples) - 1:
                result_lines.append("```\n")
        return "\n".join(result_lines)

    def read_cypher_file(self, file_path):
        """
        Opens and processes an example file.
        """
        with open(file_path) as file:
            content = file.read()

        # Split sections by one or more blank lines
        sections = re.split(r'\n\s*\n', content.strip())

        for section in sections:
            lines = section.strip().split('\n')
            information = []
            cypher = []

            # Separate comments from Cypher queries
            for line in lines:
                if line.startswith('//'):
                    information.append(line[2:].strip())
                else:
                    cypher.append(line.strip())

            # Join comment lines and query lines respectively
            info_str = '\n'.join(information)
            cypher_str = '\n'.join(cypher)

            self.examples.append({"information": info_str, "cypher": cypher_str})


class CypherExampleCollections:
    """
    Provides access to all Cypher example collections.
    """
    @classproperty
    def general_cypher_queries(self) -> CypherExampleCollection:
        return CypherExampleCollection(os.path.join(prompts_directory, "general_cypher_examples.cypher"))

    @classproperty
    def map_cypher_queries(self) -> CypherExampleCollection:
        return CypherExampleCollection(os.path.join(prompts_directory, "general_cypher_examples.cypher"))
