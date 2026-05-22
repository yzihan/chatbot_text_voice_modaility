import datetime
import json
import ast
import re

def get_current_time():
    return datetime.datetime.now()

                
def parse_to_json(resp):
    try:
        return json.loads(resp)
    except Exception as e:  # incase it the dict keys is wrapped by ' instead of "
        try:
            return ast.literal_eval(resp)
        except Exception as e:
            return extract_dict(resp)


# some helper functions to exreact number from string
def extract_single_numbers(text):
    number_pattern = re.compile(r'\b\d+\b')
    numbers = number_pattern.findall(text)
    if len(numbers) == 1:
        return numbers[0]
    else:
        raise ValueError("Multiple digit detected for single number!")
    

def extract_float_data(text):
    float_pattern = re.compile(r'\{\s*"Realistic":\s*([\d.]+),?\s*"Investigative":\s*([\d.]+),?\s*"Artistic":\s*([\d.]+),?\s*"Social":\s*([\d.]+),?\s*"Enterprising":\s*([\d.]+),?\s*"Conventional":\s*([\d.]+),?\s*\}')
    float_matches = float_pattern.findall(text)
    float_data = [{"Realistic": float(r), "Investigative": float(i), "Artistic": float(a), "Social": float(s), "Enterprising": float(e), "Conventional": float(c)} for r, i, a, s, e, c in float_matches]
    return float_data


def extract_int_data(text):
    int_pattern = re.compile(r'\{\s*"Realistic":\s*(\d+),\s*"Investigative":\s*(\d+),\s*"Artistic":\s*(\d+),\s*"Social":\s*(\d+),\s*"Enterprising":\s*(\d+),\s*"Conventional":\s*(\d+)\s*\}')
    int_matches = int_pattern.findall(text)
    int_data = [{"Realistic": int(r), "Investigative": int(i), "Artistic": int(a), "Social": int(s), "Enterprising": int(e), "Conventional": int(c)} for r, i, a, s, e, c in int_matches]
    return int_data




def extract_list(text):
    # Find the code block with the list of ratings
    list_content = re.search(r"\[(.*?)\]", text, re.DOTALL)
    
    if list_content:
        # Extract the list content and evaluate it to convert string to actual Python list
        ratings = ast.literal_eval(f"[{list_content.group(1)}]")
    else:
        return None  # Handle cases where no list is found
    
    return ratings


def extract_dict(text):
    dict_content = re.search(r"\{.*\}", text, re.DOTALL).group(0)
    
    # Convert the string to a dictionary
    trait_scores = ast.literal_eval(dict_content)
    return trait_scores
