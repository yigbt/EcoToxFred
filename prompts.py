from __future__ import annotations

import os
import re
from typing import List, Iterable
from langchain_core.prompts import PromptTemplate

import yaml
from sqlalchemy.util import classproperty

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
prompts_directory = os.path.join(current_directory, 'prompts')

graph_metadata_file = os.path.join(prompts_directory, "graph_schema_metadata.yml")


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
        if "parameters" in self.data.keys() and self.data['parameters'] is not None:
            self.parameters = set(self.data['parameters'])
        else:
            self.parameters = set()
        self.prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
        if not re.match(r"[a-z_]+", self.prompt_name):
            raise ValueError("File name of the prompt file must only contain letters and underscores.")

    def append(self, other: Prompt):
        if self is other:
            raise MemoryError("Cannot append the same Prompt to itself!")
        self.prompt += "\n" + other.prompt
        self.parameters = self.parameters.union(other.parameters)

    def inject_examples(self, examples: CypherExampleCollection):
        assert len(examples.examples) > 0
        placeholder_name = examples.get_placeholder_name()
        assert placeholder_name in self.parameters
        self.partial_apply({placeholder_name: examples.format_examples_as_markdown()})

    def has_parameter(self, parameter: str) -> bool:
        return parameter in self.parameters

    def has_parameters(self, parameters: Iterable) -> bool:
        return set(parameters).issubset(self.parameters)

    def partial_apply_prompt(self, prompt: Prompt):
        self.partial_apply({prompt.prompt_name: prompt.prompt})
        self.parameters = self.parameters.union(prompt.parameters)

    def partial_apply(self, parameters: dict):
        params_key_set = set(parameters.keys())
        assert params_key_set.issubset(set(self.parameters))
        self.prompt = self.prompt.format_map(DefaultDict(parameters))
        self.parameters = set(self.parameters) - params_key_set

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(input_variable=list(self.parameters), template=self.prompt)


# noinspection PyMethodParameters
class Prompts:
    """
    Helper class to get easy access to all prompts.

    If you add another prompt YAML file, please add the appropriate classproperty here as well.
    Also, if we create partial prompts that we need to build up by merging them,
    this would be the right place for it.
    """

    _cached_prompts = {}

    @classproperty
    def agent(cls) -> Prompt:
        """
        Provides the prompt for the agent that orchestrates all tools and delivers the final answers.
        """
        if "agent" not in cls._cached_prompts.keys():
            basic_intro = Prompt(os.path.join(prompts_directory, "basic_intro.yml"))
            cls._cached_prompts["agent"] = basic_intro
        return cls._cached_prompts["agent"]

    @classproperty
    def cypher_general(cls) -> Prompt:
        """
        Provides the prompt used for general graph database queries.
        This is used with a Cypher QA chain, and the agent relies on it when it wants to provide a text answer.
        """
        if "cypher_general" not in cls._cached_prompts.keys():
            prompt_cypher_general = Prompt(os.path.join(prompts_directory, "prompt_cypher_general.yml"))
            basic_intro = Prompt(os.path.join(prompts_directory, "basic_intro.yml"))
            cypher_intro = Prompt(os.path.join(prompts_directory, "cypher_intro.yml"))
            cypher_instructions_general = Prompt(os.path.join(prompts_directory, "cypher_instructions_general.yml"))
            prompt_cypher_general.partial_apply_prompt(basic_intro)
            prompt_cypher_general.partial_apply_prompt(cypher_intro)
            prompt_cypher_general.partial_apply_prompt(cypher_instructions_general)
            prompt_cypher_general.inject_examples(CypherExampleCollections.general_cypher_queries)
            prompt_cypher_general.partial_apply({"meta": get_graph_meta_data()})
            cls._cached_prompts["cypher_general"] = prompt_cypher_general
        return cls._cached_prompts["cypher_general"]

    @classproperty
    def cypher_map(cls) -> Prompt:
        """
        Provides the prompt used for graph database queries that access data for plotting on a map.
        The agent relies on it when it wants to provide an image of a map with annotated points.
        """
        if "cypher_map" not in cls._cached_prompts.keys():
            prompt_cypher_map = Prompt(os.path.join(prompts_directory, "prompt_cypher_map.yml"))
            basic_intro = Prompt(os.path.join(prompts_directory, "basic_intro.yml"))
            cypher_intro = Prompt(os.path.join(prompts_directory, "cypher_intro.yml"))
            cypher_instructions = Prompt(os.path.join(prompts_directory, "cypher_instructions.yml"))
            cypher_instructions_map = Prompt(os.path.join(prompts_directory, "cypher_instructions_map.yml"))
            cypher_instructions_map.partial_apply_prompt(cypher_instructions)
            prompt_cypher_map.partial_apply_prompt(basic_intro)
            prompt_cypher_map.partial_apply_prompt(cypher_intro)
            prompt_cypher_map.partial_apply_prompt(cypher_instructions_map)
            prompt_cypher_map.inject_examples(CypherExampleCollections.map_cypher_queries)
            prompt_cypher_map.partial_apply({"meta": get_graph_meta_data()})
            cls._cached_prompts["cypher_map"] = prompt_cypher_map
        return cls._cached_prompts["cypher_map"]

    @classproperty
    def cypher_plot(cls) -> Prompt:
        """
        Provides the prompt used for graph database queries that access data for plotting a two-dimensional scatter
        plot. The agent relies on it when it wants to provide an image of scientific two-dimensional plot with time
        or site names on the x-axis and any kind of numeric values on the y-axis. Numeric values can be mean or
        median concentrations, toxic units or summarized toxic units ([sum,ratio,max]TU), or driver importance values.
        """
        if "cypher_plot" not in cls._cached_prompts.keys():
            prompt_cypher_plot = Prompt(os.path.join(prompts_directory, "prompt_cypher_plot.yml"))
            basic_intro = Prompt(os.path.join(prompts_directory, "basic_intro.yml"))
            cypher_intro = Prompt(os.path.join(prompts_directory, "cypher_intro.yml"))
            cypher_instructions = Prompt(os.path.join(prompts_directory, "cypher_instructions.yml"))
            cypher_instructions_plot = Prompt(os.path.join(prompts_directory, "cypher_instructions_plot.yml"))
            cypher_instructions_plot.partial_apply_prompt(cypher_instructions)
            prompt_cypher_plot.partial_apply_prompt(basic_intro)
            prompt_cypher_plot.partial_apply_prompt(cypher_intro)
            prompt_cypher_plot.partial_apply_prompt(cypher_instructions_plot)
            prompt_cypher_plot.inject_examples(CypherExampleCollections.plot_cypher_queries)
            prompt_cypher_plot.partial_apply({"meta": get_graph_meta_data()})
            cls._cached_prompts["cypher_plot"] = prompt_cypher_plot
        return cls._cached_prompts["cypher_plot"]


class CypherExampleCollection:
    """
    CypherExampleCollection class for processing and organizing Cypher query examples from a specified file.

    It holds a number of example Cypher queries together with their corresponding descriptions.
    It can format these examples as a block of Markdown code to inject them into a prompt.
    """

    def __init__(self, example_file: str):
        """
        Reads a Cypher example file.

        :param example_file: Path to the example file.
            The file name must only contain letters and underscores.
        """
        self.examples: List[dict] = []
        self.read_cypher_file(example_file)
        self.example_name = os.path.splitext(os.path.basename(example_file))[0]
        if not re.match(r"[a-z_]+", self.example_name):
            raise ValueError("File name of the example file must only contain letters and underscores.")

    def get_queries(self) -> List[str]:
        """Returns the list of Cypher queries for this collection."""
        return [e["cypher"] for e in self.examples]

    def get_placeholder_name(self):
        """
        Returns the name of the file where the Cypher examples were read from.

        We assume that the f-string placeholder used in the prompt file has the same name.
        """
        return self.example_name

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
        """
        Provides a collection of Cypher examples for the general case typically used to access a limited number of
        results that can be presented in text form.
        """
        return CypherExampleCollection(os.path.join(prompts_directory, "cypher_fewshot_examples_general.cypher"))

    @classproperty
    def map_cypher_queries(self) -> CypherExampleCollection:
        """
        Provides a collection of Cypher examples for drawing points on a map.
        This can give in a large number of results.
        """
        return CypherExampleCollection(os.path.join(prompts_directory, "cypher_fewshot_examples_map.cypher"))

    @classproperty
    def plot_cypher_queries(self) -> CypherExampleCollection:
        """
        Provides a collection of Cypher examples used for drawing charts.
        This can give in a large number of results.
        """
        return CypherExampleCollection(os.path.join(prompts_directory, "cypher_fewshot_examples_plot.cypher"))


def get_graph_meta_data() -> str:
    """
    Reads the graph metadata from a specified file.

    :return: Graph metadata as a string.
    """
    with open(graph_metadata_file) as f:
        meta = f.read()
    return meta
















