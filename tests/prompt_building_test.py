from prompts import *


def test_prompt_loading():
    prompt = Prompts.cypher_general
    assert len(prompt.prompt) > 100
    assert prompt.parameters == {"question", "toolnames", "schema", "tools"}


def test_prompt_merging():
    prompt_1 = Prompt(os.path.join(prompts_directory, "prompt_cypher_general.yml"))
    prompt_2 = Prompt(os.path.join(prompts_directory, "prompt_cypher_map.yml"))
    len_2 = len(prompt_2.prompt)
    prompt_string_2 = str(prompt_2.prompt)
    params_2 = prompt_2.parameters
    prompt_2.append(prompt_1)
    assert len(prompt_2.prompt) == len(prompt_1.prompt) + len_2 + 1 # Newline is added as well
    assert prompt_2.prompt == prompt_string_2 + "\n" + prompt_1.prompt
    assert prompt_2.parameters == set.union(prompt_1.parameters, params_2)


def test_prompt_parameter_injection():
    prompt = Prompt(os.path.join(prompts_directory, "prompt_cypher_general.yml"))
    prompt.partial_apply({"question": "What is the capital of Germany?"})
    assert "What is the capital of Germany?" in prompt.prompt
    assert "question" not in prompt.parameters
    assert "basic_intro" in prompt.parameters
    assert "cypher_intro" in prompt.parameters
    assert "cypher_instructions_general" in prompt.parameters
    assert "cypher_fewshot_examples_general" in prompt.parameters


# This is also an example of how to inject a whole example section into a prompt.
def test_cypher_example_injection():
    prompt = Prompt(os.path.join(prompts_directory, "prompt_cypher_general.yml"))
    old_prompt_len = len(prompt.prompt)
    cypher_examples : CypherExampleCollection = CypherExampleCollections.general_cypher_queries
    prompt.inject_examples(cypher_examples)
    assert len(prompt.prompt) == (old_prompt_len +
                                  len(cypher_examples.format_examples_as_markdown()) -
                                  len(f"({cypher_examples.get_placeholder_name()})"))