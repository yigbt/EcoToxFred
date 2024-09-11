import yaml
from functools import partial
import os
import re
from typing import List

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
prompts_directory = os.path.join(current_directory, 'prompts')

class Prompt:
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
        self.parameters += other.parameters

    def partial_apply(self, parameters: dict):
        params_key_set = set(parameters.keys())
        assert params_key_set.issubset(set(self.parameters))
        self.prompt = partial(self.prompt, **parameters)
        self.parameters = set(self.parameters) - params_key_set

class CypherExamples:
    """
    CypherExamples class for processing and organizing Cypher query examples from a specified file.
    """
    def __init__(self, example_file: str):
        self.examples: List[dict] = []
        self.read_cypher_file(example_file)

    def get_queries(self):
        return [e["cypher"] for e in self.examples]

    def read_cypher_file(self, file_path):
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

def get_general_cypher_examples() -> List[dict]:
    return CypherExamples(os.path.join(prompts_directory, "general_cypher_examples.cypher")).examples

def get_map_cypher_examples() -> List[dict]:
    return CypherExamples(os.path.join(prompts_directory, "map_cypher_examples.cypher")).examples

