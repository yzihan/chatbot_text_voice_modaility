import random
from typing import List
import pandas as pd


# run application at folder path/to/project/fastapi/app. this path is relative to fastapi/app
df = pd.read_excel("Final question list - 48.xlsx") 

groups = ["HEX", "EXA", "XAC", "ACO", "COH", "OHE"]
mappings = {
    "H": "Honesty-Humility",
    "E" : "Emotionality",
    "X": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "O": "Openness to Experience"
}

def shuffle(indices: List[str]):
    random.shuffle(indices)
    return indices


def get_question_indices(group: str = "HEX"):
    selected_domains = [mappings[g] for g in group] # ['Emotionality', 'Extraversion', 'Agreeableness']

    df_selected = df[df["Domain"].isin(selected_domains)].reset_index(drop=True)
    indices = df_selected["Index"].to_list()
    return shuffle(indices) 

# for group in groups:
#     print(sorted(get_question_indices(group)))