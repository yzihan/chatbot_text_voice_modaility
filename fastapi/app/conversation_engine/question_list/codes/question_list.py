from typing import List, Dict
from conversation_engine.node import DialogNode, NodeType, Signal, summary_generator_wrapper
from conversation_engine.question_list_utils import detect, say_thank_you_and_go_next, generate_follow_up_question_1_UNINFORMATIVE, generate_follow_up_question_2_UNINFORMATIVE, generate_follow_up_question_1_NEEDS_CLARIFICATION, generate_follow_up_question_2_NEEDS_CLARIFICATION, generate_follow_up_question_1_NONSENSE, generate_follow_up_question_2_NONSENSE
from .question_nodes import *
from . import welcome_nodes as WELCOME_NODES
from .selected_questions import apply_selected_question_wording
import copy


apply_selected_question_wording(node_mappings)


def node_i_j(i: int, j: int, question_indices: List[str], node_mappings: Dict) -> DialogNode:
    """
    Given question_indices: ["F1Q2" , "F2Q12, ..."]
        where node_mappings["F1Q2"] = [node_F1Q2_0, node_F1Q2_1, node_F1Q2_2, node_F1Q2_3, node_F1Q2_4],
    
    i: index of question_indices, 1-based index
    j: index of [node_F1Q2_0, node_F1Q2_1, node_F1Q2_2, node_F1Q2_3, node_F1Q2_4],  
    return a node
    """
    question_index = question_indices[i-1]
    return node_mappings[question_index][j]




def create_quetion_nodes(question_indices: List[str]):
    node_mappings_copy = copy.deepcopy(node_mappings)
    node0_0 = copy.deepcopy(WELCOME_NODES.node0_0)
    node0_1 = copy.deepcopy(WELCOME_NODES.node0_1)
    node0_2 = copy.deepcopy(WELCOME_NODES.node0_2)
    node0_3 = copy.deepcopy(WELCOME_NODES.node0_3)
    node0_4 = copy.deepcopy(WELCOME_NODES.node0_4)
    node0_5 = copy.deepcopy(WELCOME_NODES.node0_5)
    node0_6 = copy.deepcopy(WELCOME_NODES.node0_6)
    node0_7 = copy.deepcopy(WELCOME_NODES.node0_7)

    node_ending = copy.deepcopy(WELCOME_NODES.node_ending)
    node_exiting = copy.deepcopy(WELCOME_NODES.node_exiting)
    node_exiting_1 = copy.deepcopy(WELCOME_NODES.node_exiting_1)
    node_exiting_2 = copy.deepcopy(WELCOME_NODES.node_exiting_2)
    node_exiting_3 = copy.deepcopy(WELCOME_NODES.node_exiting_3)



    # ---------------------------------------------------------------------------- #
    # ------------------------------------ links ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node0_0.add_next_node("default", node0_1)
    node0_1.add_next_node("default", node0_2)
    node0_2.add_next_node("default", node0_3)
    node0_3.add_next_node("default", node0_4)
    node0_4.add_next_node("default", node0_5)
    node0_5.add_next_node("default", node0_6)
    node0_6.add_next_node("default", node0_7)
    node0_7.add_next_node("default", node_i_j(1, 0, question_indices, node_mappings_copy))


    # ------------------------- 1 to 23 -------------------------------
    for i in range(1, 24): 
        node_i_0 = node_i_j(i, 0, question_indices, node_mappings_copy)
        node_i_1 = node_i_j(i, 1, question_indices, node_mappings_copy)
        node_i_2 = node_i_j(i, 2, question_indices, node_mappings_copy)
        node_i_3 = node_i_j(i, 3, question_indices, node_mappings_copy)
        node_i_4 = node_i_j(i, 4, question_indices, node_mappings_copy)

        node_i_0.info["progress"] = i
        node_i_1.info["progress"] = i
        node_i_2.info["progress"] = i
        node_i_3.info["progress"] = i     
        node_i_4.info["progress"] = i  

        connect_question_prompt(node_i_0, node_i_1, node_i_2)

        node_i_2.add_next_node("NEEDS_CLARIFICATION", node_i_3)
        node_i_2.add_next_node("NONSENSE", node_i_3)
        node_i_2.add_next_node("UNINFORMATIVE", node_i_3)
        node_i_2.add_next_node("VALID", node_i_j(i+1, 0, question_indices, node_mappings_copy))
        node_i_2.add_next_node("DECLINE_CONTINUE", node_exiting)

        node_i_3.add_next_node("NEEDS_CLARIFICATION", node_i_4)
        node_i_3.add_next_node("NONSENSE", node_i_4)
        node_i_3.add_next_node("UNINFORMATIVE", node_i_4)
        node_i_3.add_next_node("VALID", node_i_j(i+1, 0, question_indices, node_mappings_copy))
        node_i_3.add_next_node("DECLINE_CONTINUE", node_exiting)

        node_i_4.add_next_node("default", node_i_j(i+1, 0, question_indices, node_mappings_copy))
    



    # ------------------------- last q: 24 -------------------------------
    node_last_0 = node_i_j(len(question_indices), 0, question_indices, node_mappings_copy)
    node_last_1 = node_i_j(len(question_indices), 1, question_indices, node_mappings_copy)
    node_last_2 = node_i_j(len(question_indices), 2, question_indices, node_mappings_copy)
    node_last_3 = node_i_j(len(question_indices), 3, question_indices, node_mappings_copy)
    node_last_4 = node_i_j(len(question_indices), 4, question_indices, node_mappings_copy)

    connect_question_prompt(node_last_0, node_last_1, node_last_2)

    node_last_2.add_next_node("NEEDS_CLARIFICATION", node_last_3)
    node_last_2.add_next_node("NONSENSE", node_last_3)
    node_last_2.add_next_node("UNINFORMATIVE", node_last_3)
    node_last_2.add_next_node("VALID", node_ending)
    node_last_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node_last_3.add_next_node("NEEDS_CLARIFICATION", node_last_4)
    node_last_3.add_next_node("NONSENSE", node_last_4)
    node_last_3.add_next_node("UNINFORMATIVE", node_last_4)
    node_last_3.add_next_node("VALID", node_ending)
    node_last_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node_last_4.add_next_node("default", node_ending)
    

    # ------------------------ decline ---------------------------
    node_exiting.add_next_node("default", node_exiting_1)
    node_exiting_1.add_next_node("default", node_exiting_2)
    node_exiting_2.add_next_node("default", node_exiting_3)

    return node0_0


def connect_question_prompt(node_0: DialogNode, node_1: DialogNode, node_2: DialogNode) -> None:
    if node_1.text.strip():
        node_0.add_next_node("default", node_1)
        node_1.add_next_node("default", node_2)
    else:
        node_0.add_next_node("default", node_2)
