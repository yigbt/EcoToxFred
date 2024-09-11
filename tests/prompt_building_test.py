from prompts import Prompts, CypherExampleCollections, CypherExampleCollection


def test_prompt_loading():
    prompt = Prompts.general_cypher_prompt
    assert len(prompt.prompt) > 2000
    assert prompt.parameters == {"examples", "question", "schema"}


def test_prompt_merging():
    prompt_1 = Prompts.general_cypher_prompt
    prompt_2 = Prompts.general_cypher_prompt
    prompt_2.append(prompt_1)
    assert len(prompt_2.prompt) >= 2*len(prompt_1.prompt)
    assert prompt_2.prompt == prompt_1.prompt + "\n" + prompt_1.prompt
    assert prompt_2.parameters == prompt_1.parameters


def test_prompt_parameter_injection():
    prompt = Prompts.general_cypher_prompt
    prompt.partial_apply({"question": "What is the capital of Germany?"})
    assert "What is the capital of Germany?" in prompt.prompt
    assert "examples" in prompt.parameters
    assert "schema" in prompt.parameters
    assert "question" not in prompt.parameters


# This is also an example of how to inject a whole example section into a prompt.
def test_cypher_example_injection():
    prompt = Prompts.general_cypher_prompt
    old_prompt_len = len(prompt.prompt)
    cypher_examples : CypherExampleCollection = CypherExampleCollections.general_cypher_queries
    prompt.inject_examples(cypher_examples)
    assert len(prompt.prompt) == old_prompt_len + len(cypher_examples.format_examples_as_markdown()) - len("{examples}")