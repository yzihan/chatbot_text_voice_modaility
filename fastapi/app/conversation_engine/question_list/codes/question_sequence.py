from typing import List
from .selected_questions import (
    SELECTED_QUESTION_INDICES,
    get_randomized_selected_question_indices,
)

groups = ["HEX", "EXA", "XAC", "ACO", "COH", "OHE"]
mappings = {
    "H": "Honesty-Humility",
    "E" : "Emotionality",
    "X": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "O": "Openness to Experience"
}

def get_question_indices(group: str = "HEX"):
    return get_randomized_selected_question_indices()


def get_selected_question_indices() -> List[str]:
    return SELECTED_QUESTION_INDICES.copy()

# for group in groups:
#     print(sorted(get_question_indices(group)))
