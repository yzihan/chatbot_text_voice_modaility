import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conversation_engine.question_list.codes.question_list import create_quetion_nodes  # noqa: E402
from conversation_engine.question_list.codes.question_nodes import node_mappings  # noqa: E402
from conversation_engine.question_list.codes.question_sequence import (  # noqa: E402
    get_question_indices,
    get_selected_question_indices,
)
from conversation_engine.question_list.codes.selected_questions import (  # noqa: E402
    SELECTED_QUESTION_WORDING,
)


def test_selected_question_set_has_one_question_per_facet():
    selected = get_selected_question_indices()
    facets = {question_index.split("Q")[0] for question_index in selected}

    assert len(selected) == 24
    assert len(facets) == 24
    assert set(selected) == set(SELECTED_QUESTION_WORDING)
    assert set(selected).issubset(node_mappings)


def test_new_sessions_use_same_questions_in_random_order():
    selected = set(get_selected_question_indices())
    orders = [get_question_indices("HEX") for _ in range(8)]

    assert all(len(order) == 24 for order in orders)
    assert all(set(order) == selected for order in orders)
    assert len({tuple(order) for order in orders}) > 1


def test_selected_question_wording_is_applied_to_chat_nodes():
    question_index = "F23Q2"
    intro_node, middle_node, prompt_node = node_mappings[question_index][:3]

    assert intro_node.text.startswith("When people face a challenge")
    assert middle_node.text == ""
    assert prompt_node.text == "Feel free to share an example if one comes to mind."

    root = create_quetion_nodes(get_selected_question_indices())
    assert root.id == "0_0"
