from typing import List
from conversation_engine.node import DialogNode, NodeType, Signal, summary_generator_wrapper
from conversation_engine.question_list_utils import detect, say_thank_you_and_go_next, generate_follow_up_question_1_UNINFORMATIVE, generate_follow_up_question_2_UNINFORMATIVE, generate_follow_up_question_1_NEEDS_CLARIFICATION, generate_follow_up_question_2_NEEDS_CLARIFICATION, generate_follow_up_question_1_NONSENSE, generate_follow_up_question_2_NONSENSE


# ---------------------------------------------------------------------------- #
# ------------------------------------ Q0 ------------------------------------ #
# ---------------------------------------------------------------------------- #
node0_0 = DialogNode(
    id="0_0",
    text= "Hi there! I’m Nova. I was designed to learn more about your personality by asking a few questions. Please rest assured that your response will be kept confidential — your responses won’t be shared with anyone outside this study. This space is just for you, so please feel free to express yourself openly and honestly.",
    node_type=NodeType.PLAIN_MESSAGE,
    info={"progress": 0},
)

node0_1 = DialogNode(
    id="0_1",
    text= "Before we begin, how should I address you in this chat? You can just use a nickname or any name you prefer.",
    node_type=NodeType.NO_CONDITION_CHECK,
    summary_generators={
        "default": lambda chatting_messages : summary_generator_wrapper(chatting_messages, "Reply to user's name. Response something like 'Got it, thanks <username>!', 'Hi, <usernmae>!', 'It is really nice to chat with you, <username>!'."),
    },
    info={"progress": 0},
)

node0_2 = DialogNode(
    id="0_2",
    text= "Before I start the interview. Let’s start with something easy. What do you usually like to do for fun or to relax in your free time?",
    node_type=NodeType.NO_CONDITION_CHECK,
    summary_generators={
        "default": lambda chatting_messages : summary_generator_wrapper(chatting_messages, "Provide an acknowledgement based on user input to maintain smooth conversation. Do not ask quesions, simply reply to user."),
    },
    info={"progress": 0},
)

node0_3 = DialogNode(
    id="0_3",
    text= "What do you do these days? Are you working, studying, or doing something else?",
    node_type=NodeType.NO_CONDITION_CHECK,
    summary_generators={
        "default": lambda chatting_messages : summary_generator_wrapper(chatting_messages, "Provide an acknowledgement based on user input to maintain smooth conversation. Do not ask quesions, simply reply to user."),
    },
    info={"progress": 0},
)

node0_4 = DialogNode(
    id="0_4",
    text= "Thanks for chatting with me so far! 😊",
    node_type=NodeType.PLAIN_MESSAGE,
    info={"progress": 0},
)

node0_5 = DialogNode(
    id="0_5",
    text= "Now we’re about to start the main part of our conversation. I’ll ask you a few open-ended questions to learn more about your personality—things like how you usually think, feel, or act in different situations.",
    node_type=NodeType.PLAIN_MESSAGE,
    info={"progress": 0},
)

node0_6 = DialogNode(
    id="0_6",
    text= "Sometimes I might take a moment to respond—so thanks in advance for your patience! ",
    node_type=NodeType.PLAIN_MESSAGE,
    info={"progress": 0},
)

node0_7 = DialogNode(
    id="0_7",
    text= "Let’s get started!",
    node_type=NodeType.PLAIN_MESSAGE,
    info={"progress": 0},
)


# ---------------------------------------------------------------------------- #
# ------------------------------------ Qlast ------------------------------------ #
# ---------------------------------------------------------------------------- #
node_ending = DialogNode(
    id="-1",
    text="Thank you so much for taking the time to answer these questions! We really appreciate your responses. If you have any questions or would like to follow up, feel free to reach out at zihan25@illinois.edu. Wishing you a wonderful day ahead!",
    node_type=NodeType.END_NODE
)

# ---------------------------------------------------------------------------- #
# ------------------------------------ DECLINE CONTINUE ------------------------------------ #
# ---------------------------------------------------------------------------- #
node_exiting = DialogNode(
    id="-2_0",
    text= "I understand—it’s totally okay to feel tired.",
    node_type=NodeType.PLAIN_MESSAGE,
)
node_exiting_1 = DialogNode(
    id="-2_1",
    text= "If you’d like to stop now, you can click the “Stop” button at the top right corner to exit the interview.",
    node_type=NodeType.PLAIN_MESSAGE,
)
node_exiting_2 = DialogNode(
    id="-2_2",
    text= "If you decide to continue later, please make sure to log back in using the same participant ID. Then, instead of starting a new conversation, click the “History” button and select this interview session to resume where you left off.",
    node_type=NodeType.PLAIN_MESSAGE,
)
node_exiting_3 = DialogNode(
    id="-2_3",
    text= "Thank you for your time so far!",
    node_type=NodeType.END_NODE,
)
