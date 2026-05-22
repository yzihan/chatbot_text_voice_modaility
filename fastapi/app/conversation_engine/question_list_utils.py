from .node import *
from .openai_api import send_prompt, send_messages
import copy
from .utils import parse_to_json


def detect(chatting_messages: List[Dict[str, str]]) -> str:
    """
    最后一条message是user response,
    往前3条是问题 
    """
    question, response = chatting_messages[-4]["content"] + " " + chatting_messages[-3]["content"] + " " + chatting_messages[-2]["content"], chatting_messages[-1]["content"]

    prompt = f"""Above is a conversation. ou are evaluating a participant’s response to a personality interview question. Classify the response into one of the following categories:
VALID: The answer is relevant, meaningful, and usable for assessing personality.
UNINFORMATIVE: The answer is relevant but too short or vague to assess personality traits.
NONSENSE: The answer is irrelevant, off-topic, or meaningless.
NEEDS_CLARIFICATION: The answer expresses confusion, misunderstanding, or inability to think of an example (e.g., "What do you mean?", "I don’t know", "I can’t think of anything").
DECLINE_CONTINUE: The participant expresses fatigue, unwillingness, or refusal to continue (e.g., "I'm tired," "I want to stop," "Can I be done?").

Question: {question}
Response: {response}

Return the category in the following python Dict format: {{ "category": str }}"""
    

    messages = copy.deepcopy(chatting_messages)
    messages.append({"role": "system", "content": prompt})
    resp = send_messages(messages, model = "gpt-4o-mini")

    # resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  detect response: ", resp)
    print("-"*100)
    print()

    try:
        return parse_to_json(resp)["category"]
    except Exception as e:
        print("Error parsing openai resp")
        return "NA"
    
def say_thank_you_and_go_next(chatting_messages: List[Dict[str, str]]) -> str:
    """
    最后一条message是user response,
    倒数3条是问题    
    """
    question, response = chatting_messages[-4]["content"] + " " + chatting_messages[-3]["content"] + " " + chatting_messages[-2]["content"], chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a standardized personality assessment. The participant has just provided a valid and meaningful answer. Your task is to respond with a brief, neutral thank-you message and smoothly transition to the next question.

Instructions:
- Acknowledge the participant’s input without evaluating it.
- To reduce social desirability bias, avoid saying the answer was “good,” or “interesting.” Instead, use neutral acknowledgment (e.g., “Thanks for sharing”).
- Do not reflect on or summarize the content of the response.
- Do not include the next question in your output.
- Keep your message concise (no more than 2 sentences).
- Vary the phrasing to maintain a natural, human-like tone across turns.


Here is the original question:
{question}

Here is the participant's response:
{response}

Output only the thank-you message and transition."""
    
    messages = copy.deepcopy(chatting_messages)
    messages.append({"role": "system", "content": prompt})
    
    resp = send_messages(messages, model = "gpt-4o-mini")
    print("###  say_thank_you_and_go_next response: ", resp)
    # resp = send_prompt(prompt, model = "gpt-4o-mini")
    try:
        return resp
    except Exception as e:
        print(f"Error Generating LLM response: {e}")
        return "NA"


def generate_follow_up_question_1_UNINFORMATIVE(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], question_index: int = -2, **kargs) -> str:
    """
    最后一条message是user response,
    往前3条是问题 
    """
    question, response = complete_chatting_messages[-4]["content"] + " " + complete_chatting_messages[-3]["content"] + " " + complete_chatting_messages[-2]["content"], complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a personality assessment. The participant has given a response that is relevant but too brief or vague to be meaningfully interpreted. Your task is to gently prompt them to elaborate, ideally by inviting a more detailed explanation or a concrete example.

Guidelines:
-Acknowledge the participant’s effort using warm but neutral language.
-Encourage further detail in a non-judgmental and conversational tone.
-Avoid any wording that implies the current response is insufficient or wrong. Instead, frame your prompt as an invitation to expand.
-If appropriate, suggest specific ways to elaborate (e.g., “a situation,” “what you were thinking,” etc.).
-Keep your message brief and natural—no more than 2 sentences.
-Vary phrasing across interviews to avoid sounding scripted or repetitive.


Here is the original question:
{question}

Here is the participant's answer:
{response}

Output only the follow-up question."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_1_UNINFORMATIVE response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp


def generate_follow_up_question_2_UNINFORMATIVE(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], **kargs) -> str:
    """
    最后一条message是user response,
    是第二次追问： q1-1, q1-2, q1-3, res-1, q2, res2
    """
    question = complete_chatting_messages[-6]["content"] + " " + complete_chatting_messages[-5]["content"] + " " + complete_chatting_messages[-4]["content"]
    response1 = complete_chatting_messages[-3]["content"]
    response2 = complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a personality assessment. The participant has given a response that is relevant but too brief or vague to be meaningfully interpreted. Your task is to gently prompt them to elaborate, ideally by inviting a more detailed explanation or a concrete example.

Guidelines:
-Acknowledge the participant’s effort using warm but neutral language.
-Encourage further detail in a non-judgmental and conversational tone.
-Avoid any wording that implies the current response is insufficient or wrong. Instead, frame your prompt as an invitation to expand.
-If appropriate, suggest specific ways to elaborate (e.g., “a situation,” “what you were thinking,” etc.).
-Keep your message brief and natural—no more than 2 sentences.
-Vary phrasing across interviews to avoid sounding scripted or repetitive.

Here is the original question:
{question}

Here are the participant's answers:
- {response1}
- {response2}

Output only the follow-up question."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_2_UNINFORMATIVE response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp


def generate_follow_up_question_1_NEEDS_CLARIFICATION(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], question_index: int = -2, **kargs) -> str:
    """
    最后一条message是user response,
    往前3条是问题 
    """
    question, response = complete_chatting_messages[-4]["content"] + " " + complete_chatting_messages[-3]["content"] + " " + complete_chatting_messages[-2]["content"], complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a personality assessment. The participant has given a response that is relevant but too brief or vague to be meaningfully interpreted. Your task is to gently prompt them to elaborate, ideally by inviting a more detailed explanation or a concrete example.

Guidelines:
-Acknowledge the participant’s confusion in a warm, non-judgmental way.
-Restate or slightly rephrase the original question while preserving its meaning and structure.
-Do not explain, interpret, or give examples.
-After repeating the question, briefly confirm whether the participant now understands.
-Keep your message concise.

Here is the original question:
{question}

Here is the participant's answer:
{response}

Return only the follow-up message, which includes (1) gentle acknowledgment, (2) a repeat or light rewording of the question, and (3) a soft confirmation check.
Output only the follow-up message."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_1_NEEDS_CLARIFICATION response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp


def generate_follow_up_question_2_NEEDS_CLARIFICATION(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], **kargs) -> str:
    """
    最后一条message是user response,
    是第二次追问： q1-1, q1-2, q1-3, res-1, q2, res2
    """
    question = complete_chatting_messages[-6]["content"] + " " + complete_chatting_messages[-5]["content"] + " " + complete_chatting_messages[-4]["content"]
    response1 = complete_chatting_messages[-3]["content"]
    response2 = complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a personality assessment. The participant has given a response that is relevant but too brief or vague to be meaningfully interpreted. Your task is to gently prompt them to elaborate, ideally by inviting a more detailed explanation or a concrete example.

Guidelines:
-Acknowledge the participant’s confusion in a warm, non-judgmental way.
-Restate or slightly rephrase the original question while preserving its meaning and structure.
-Do not explain, interpret, or give examples.
-After repeating the question, briefly confirm whether the participant now understands.
-Keep your message concise.

Here is the original question:
{question}

Here are the participant's answers:
- {response1}
- {response2}

Return only the follow-up message, which includes (1) gentle acknowledgment, (2) a repeat or light rewording of the question, and (3) a soft confirmation check.
Output only the follow-up message."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_2_NEEDS_CLARIFICATION response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp



def generate_follow_up_question_1_NONSENSE(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], question_index: int = -2, **kargs) -> str:
    """
    最后一条message是user response,
    往前3条是问题 
    """
    question, response = complete_chatting_messages[-4]["content"] + " " + complete_chatting_messages[-3]["content"] + " " + complete_chatting_messages[-2]["content"], complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a standardized personality assessment. The participant’s response appears off-topic, incoherent, or unrelated to the question. Your task is to:
-Gently acknowledge the participant’s effort.
-Indicate, in a respectful and neutral way, that the response did not seem related to the question.
-Invite the participant to try again with a response based on their own experience.
-Do not interpret the question or give examples.
-Keep your message brief and supportive, no more than 2 sentences.


Here is the original question:
{question}

Here is the participant's answer:
{response}

Return a follow-up message that includes:
-A soft, respectful acknowledgment that the response seemed unrelated
-An invitation to answer again, ideally using a real-life example

Output only the follow-up message."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_1_NONSENSE response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp


def generate_follow_up_question_2_NONSENSE(current_node: DialogNode, parallism_work_results: Dict, condition: str, complete_chatting_messages: List[Message], **kargs) -> str:
    """
    最后一条message是user response,
    是第二次追问： q1-1, q1-2, q1-3, res-1, q2, res2
    """
    question = complete_chatting_messages[-6]["content"] + " " + complete_chatting_messages[-5]["content"] + " " + complete_chatting_messages[-4]["content"]
    response1 = complete_chatting_messages[-3]["content"]
    response2 = complete_chatting_messages[-1]["content"]

    prompt = f"""You are a friendly and professional interviewer conducting a standardized personality assessment. The participant’s response appears off-topic, incoherent, or unrelated to the question. Your task is to:
-Gently acknowledge the participant’s effort.
-Indicate, in a respectful and neutral way, that the response did not seem related to the question.
-Invite the participant to try again with a response based on their own experience.
-Do not interpret the question or give examples.
-Keep your message brief and supportive, no more than 2 sentences.

Here is the original question:
{question}

Here are the participant's answers:
- {response1}
- {response2}

Return a follow-up message that includes:
-A soft, respectful acknowledgment that the response seemed unrelated
-An invitation to answer again, ideally using a real-life example

Output only the follow-up message."""
    
    resp = send_prompt(prompt, model = "gpt-4o-mini")
    print("###  generate_follow_up_question_2_NONSENSE response: ", resp)
    next_node = current_node.next_nodes[condition]
    next_node.text = resp


