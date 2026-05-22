from __future__ import annotations
from typing import List, Dict, Callable, Optional, Union, TypedDict, Any
from enum import Enum, auto
import uuid
import copy
from .openai_api import send_messages
from .utils import parse_to_json
from collections import defaultdict



# ---------------------------------------------------------------------------- #
# ------------------------------------ types------------------------------------ #
# ---------------------------------------------------------------------------- #
class Message(TypedDict):
    role: str
    content: str

NodeQuestion = Union[str, Callable[[str], str]]

# use signals to pass summary, condition check, parallism, etc
class Signal(Enum):
    SKIP_SUMMARY_SIGNAL = auto()


class NodeType(Enum):
    DEFAULT_QUESTION = auto()     # Standard default question node
    NO_CONDITION_CHECK = auto()   # no oncdition check, still perform parallism and summary. Condition must be default
    PLAIN_MESSAGE = auto()        # Send question, do not expect response, enter next
    SELECTION_QUESTION = auto()   # Multiple choice node
    END_NODE = auto()             # Conversation termination


class SelectionOption:
    """Option structure for selection questions"""

    def __init__(
        self,
        text: str,
        next_node: Optional['DialogNode'] = None,
        is_others: bool = False,
        clarification_prompt: Optional[str] = None
    ):
        self.text = text
        self.next_node = next_node
        self.is_others = is_others
        self.clarification_prompt = clarification_prompt


ParallelismWork = Callable[[Any], Any]

# ---------------------------------------------------------------------------- #
# ------------------------------------ node ------------------------------------ #
# ---------------------------------------------------------------------------- #



class DialogNode:
    """Enhanced dialog node structure"""

    def __init__(
        self,
        id: Optional[str] = None,
        text: NodeQuestion = "",
        node_type: NodeType = NodeType.DEFAULT_QUESTION,  
        options: Optional[List[SelectionOption]] = None,
        max_clarification_attempts: int = 1,
        default_clarification_prompt: str = "Could you please give me an clear answer on this question?",
        condition_check: Optional[Callable[..., str]] = None,
        summary_generators: Optional[Dict[str, Union[Callable[..., str], 'Signal', str]]] = None,
        next_nodes: Optional[Dict[Union[bool, str], 'DialogNode']] = None,
        
        parallism_works: Optional[Dict[str, List['ParallelismWork']]] = None,
        info: Dict[str, Any] = {},
    ):
        # ID handling
        self.id = id if id is not None else str(uuid.uuid4())

        # Basic attributes
        self.text = text
        self.chatting_messsages: List['Message'] = []  # the conversation between user and ai on this node

        self.node_type = node_type


        self.options = options if options is not None else []
        self.max_clarification_attempts = max_clarification_attempts
        self.default_clarification_prompt = default_clarification_prompt

        if condition_check is None:
            condition_check = lambda x: "default"
        self.condition_check = condition_check

        self.summary_generators = summary_generators if summary_generators is not None else {}
        self.next_nodes = next_nodes if next_nodes is not None else {}

        # parallism_works 用 defaultdict(list)
        self.parallism_works = defaultdict(list)
        if parallism_works is not None:
            for key, val in parallism_works.items():
                self.parallism_works[key] = val

        # set is end of lie
        self.eof = False
        if self.node_type in [NodeType.PLAIN_MESSAGE, NodeType.END_NODE]:
            self.eof = True

        # store tags for this question
        self.info = info

    def add_option(self, 
                   option_text: str, 
                   next_node: Optional[DialogNode] = None, 
                   is_others: bool = False, 
                   clarification_prompt: Optional[str] = None) -> DialogNode:
        """Add selection question option"""
        self.node_type = NodeType.SELECTION_QUESTION
        self.options.append(SelectionOption(
            text=option_text, 
            next_node=next_node, 
            is_others=is_others,
            clarification_prompt=clarification_prompt or self.default_clarification_prompt
        ))
        return self
    
    def add_next_node(self, condition: Union[bool, str], node: DialogNode) -> DialogNode:
        """Add next node based on condition"""
        self.next_nodes[condition] = node

    
    def set_summary_generator(self, condition: Union[bool, str], generator: Callable[[str], str]) -> DialogNode:
        """Set summary generator for a condition"""
        self.summary_generators[condition] = generator
        return self
    
    def __str__(self) -> str:
        # return f"Current node question: {self.text}        Next nodes: { [(key, val.text) for key, val in self.next_nodes.items()] }"
        return f"{self.id}"

    def to_string(self) -> str:
        return self.__str__()
    





def condition_check_wrapper(chatting_messages: List[Dict[str, str]], condition_check_prompt: str) -> str:
    chatting_messages_copy = copy.deepcopy(chatting_messages)
    chatting_messages_copy.append({
        "role": "system",
        "content": f"""Based on above user response, judge which category the user response belongs to. Here are the rules. {condition_check_prompt}. If user response is not answering the question or cannot be understood or does not belong to previous categories, the categroy is "NA". Return your response in the following python Dict format: {{ "category": str }}"""
    })
    print(" Send LLM Request ".center(100, "="))
    print("### Mesages: ", chatting_messages_copy)

    resp = send_messages(chatting_messages_copy, model = "gpt-4o-mini")
    print("### Response: ", resp)
    print("-"*100)
    print()

    try:
        return parse_to_json(resp)["category"]
    except Exception as e:
        print("Error parsing openai resp")
        return "NA"
    

def summary_generator_wrapper(chatting_messages: List[Dict[str, str]], summary_instruction_prompt: str) -> str:
    chatting_messages_copy = copy.deepcopy(chatting_messages)
    chatting_messages_copy.append({
        "role": "system",
        "content": f"""Based on previous conversation, fill the conversation and write a short response to the user. Here is what your response should be about: {summary_instruction_prompt}. Constraint your response within 25 words. You should not answer a question but should simply reply to the user. Return in the following python Dict format: {{ "response": str }}"""
    })
    print(" Send LLM Request ".center(100, "="))
    print("### Mesages: ", chatting_messages_copy)

    resp = send_messages(chatting_messages_copy, model = "gpt-4o-mini")
    print("### Response: ", resp)
    print("-"*100)
    print()

    try:
        return parse_to_json(resp)["response"]
    except Exception as e:
        print("Error parsing openai resp")
        return "NA"
