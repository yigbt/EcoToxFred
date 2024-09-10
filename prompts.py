import yaml
from functools import partial
import re
from typing import List

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

    def read_cypher_file(self, file_path):
        with open(file_path, 'r') as file:
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
            info_str = ' '.join(information)
            cypher_str = ' '.join(cypher)

            self.examples.append({"information": info_str, "cypher": cypher_str})
