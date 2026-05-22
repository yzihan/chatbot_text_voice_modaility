
from conversation_engine.node import DialogNode, NodeType, Signal, summary_generator_wrapper
from conversation_engine.question_list_utils import detect, say_thank_you_and_go_next, generate_follow_up_question_1_UNINFORMATIVE, generate_follow_up_question_2_UNINFORMATIVE, generate_follow_up_question_1_NEEDS_CLARIFICATION, generate_follow_up_question_2_NEEDS_CLARIFICATION, generate_follow_up_question_1_NONSENSE, generate_follow_up_question_2_NONSENSE


def create_new_quetion_list():

    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q0 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node0_0 = DialogNode(
        id="0_0",
        text= "Hi there! I’m Nova. I was designed to learn more about your personality by asking a few questions.",
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
    # ------------------------------------ Q1 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node1_0 = DialogNode(
        id="1_0",
        text="Sometimes, we need help or support from people we don’t particularly like or get along with. Think of a time when you needed something—information, assistance, or a favor—from someone you didn’t like or know well.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 1 },
    )

    node1_1 = DialogNode(
        id="1_1",
        text="How did you approach that person, and how genuine were you in how you acted?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 1 },
    )
    
    node1_2 = DialogNode(
        id="1_2",
        text="If you haven’t experienced this, describe how you think you would handle such a situation.",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 1 },
    )

    node1_3 = DialogNode(
        id="1_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 1 },
    )


    node1_4 = DialogNode(
        id="1_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 1 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q2 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node2_0 = DialogNode(
        id="2_0",
        text="Sometimes in everyday life, people receive things they didn’t earn—like being given too much change or gaining access to something they didn’t pay for. Think of a time when you received something you didn’t expect or deserve—such as extra money, a mistaken refund, or an unearned benefit.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 2 },
    )

    node2_1 = DialogNode(
        id="2_1",
        text="Please describe exactly what happened, how you responded, and how you felt.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 2 },
    )
    
    node2_2 = DialogNode(
        id="2_2",
        text="If nothing like this has happened to you, please describe how you think you would feel and act if it did.",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 2 },
    )

    node2_3 = DialogNode(
        id="2_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 2 },
    )


    node2_4 = DialogNode(
        id="2_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 2 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q3 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node3_0 = DialogNode(
        id="3_0",
        text="Sometimes we find ourselves in a position where we can afford something expensive—like luxury clothing, the newest electronics, or a high-end experience—even if we don’t really need it. This might happen after getting a raise, receiving a bonus or gift, or simply having extra savings.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 3 },
    )

    node3_1 = DialogNode(
        id="3_1",
        text="Can you think of a time when you had the option to spend money on something that would show wealth or status? What did you choose to do, and what were your honest thoughts and feelings behind that choice?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 3 },
    )
    
    node3_2 = DialogNode(
        id="3_2",
        text="If no situation comes to mind, how do you think you’d respond in that kind of moment?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 3 },
    )

    node3_3 = DialogNode(
        id="3_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 3 },
    )


    node3_4 = DialogNode(
        id="3_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 3 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q4 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node4_0 = DialogNode(
        id="4_0",
        text="Sometimes, people are given special privileges—like skipping a line, receiving VIP treatment, or being treated differently because of their status, title, or accomplishments.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 4 },
    )

    node4_1 = DialogNode(
        id="4_1",
        text="Think of a time when you were offered or expected to receive special treatment. How did you feel about it, and how did you respond?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 4 },
    )
    
    node4_2 = DialogNode(
        id="4_2",
        text="If this hasn’t happened to you, describe how you think you would react.",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 4 },
    )

    node4_3 = DialogNode(
        id="4_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 4 },
    )


    node4_4 = DialogNode(
        id="4_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 4 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q5 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node5_0 = DialogNode(
        id="5_0",
        text="Sometimes we find ourselves needing to go somewhere despite unsafe or risky conditions—like driving through a snowstorm, walking alone at night, or traveling during a weather alert.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 5 },
    )

    node5_1 = DialogNode(
        id="5_1",
        text="Can you think of a time when you had to decide whether or not to go through with something like that? What did you end up doing, and how did you feel about the risk in that moment?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 5 },
    )
    
    node5_2 = DialogNode(
        id="5_2",
        text="If no specific situation comes to mind, how do you think you would respond if you were faced with that kind of risky condition?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 5 },
    )

    node5_3 = DialogNode(
        id="5_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 5 },
    )


    node5_4 = DialogNode(
        id="5_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 5 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q6 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node6_0 = DialogNode(
        id="6_0",
        text="Waiting to hear back about something important—like a job application, test results, or medical news—can be stressful for some people, while others stay pretty calm.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 6 },
    )

    node6_1 = DialogNode(
        id="6_1",
        text="Think of a time when you were waiting for an important decision or outcome. What was that experience like for you? How did it affect your thoughts, emotions, or behavior?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 6 },
    )
    
    node6_2 = DialogNode(
        id="6_2",
        text="If no situation comes to mind, describe how you think you'd typically respond.",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 6 },
    )

    node6_3 = DialogNode(
        id="6_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 6 },
    )


    node6_4 = DialogNode(
        id="6_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 6 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q7 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node7_0 = DialogNode(
        id="7_0",
        text="During times of stress or uncertainty—like waiting for results, facing an unresolved issue, or managing a complex situation—people vary in how much they want to talk about it with others.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 7 },
    )

    node7_1 = DialogNode(
        id="7_1",
        text="Can you think of a time when something was on your mind and you were unsure how it would turn out? What were your thoughts and emotions, and how did you feel about involving someone else? What helped you most in that situation?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 7 },
    )
    
    node7_2 = DialogNode(
        id="7_2",
        text="If nothing specific comes to mind, how do you think you would feel about sharing something like that with others?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 7 },
    )

    node7_3 = DialogNode(
        id="7_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 7 },
    )


    node7_4 = DialogNode(
        id="7_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 7 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q8 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node8_0 = DialogNode(
        id="8_0",
        text="Sometimes, when someone we care about is deeply upset—like going through a breakup, family loss, or intense stress—people respond in very different ways. Some feel almost as if they’re carrying the other person’s pain, while others remain more emotionally separate.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 8 },
    )

    node8_1 = DialogNode(
        id="8_1",
        text="Can you think of a time when someone close to you was going through something difficult? How did their emotions affect you, and how did you respond?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 8 },
    )
    
    node8_2 = DialogNode(
        id="8_2",
        text="If nothing specific comes to mind, how do you think you'd typically feel in that kind of situation?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 8 },
    )

    node8_3 = DialogNode(
        id="8_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 8 },
    )


    node8_4 = DialogNode(
        id="8_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 8 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q9 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node9_0 = DialogNode(
        id="9_0",
        text="In social situations—like group projects, team meetings, or informal gatherings—people often get a sense of whether others enjoy being around them. Think of a time when you were in a group setting—like a class, meeting, or social gathering—and noticed how others were interacting with you.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 9 },
    )

    node9_1 = DialogNode(
        id="9_1",
        text="What gave you that impression, and did it influence how you acted or felt in the moment?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 9 },
    )
    
    node9_2 = DialogNode(
        id="9_2",
        text="If no example comes to mind, describe how you usually feel when you're part of a group conversation or activity.",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 9 },
    )

    node9_3 = DialogNode(
        id="9_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 9 },
    )


    node9_4 = DialogNode(
        id="9_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 9 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q10 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node10_0 = DialogNode(
        id="10_0",
        text="In everyday life, we sometimes meet people we don’t know—like at events, work, or in line somewhere. Some people easily start conversations, while others feel more hesitant.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 10 },
    )

    node10_1 = DialogNode(
        id="10_1",
        text="Can you think of a time when you introduced yourself to someone new or started a conversation in an unfamiliar setting? What was that experience like for you—did you feel comfortable or nervous?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 10 },
    )
    
    node10_2 = DialogNode(
        id="10_2",
        text="If you haven’t been in that situation recently, how do you think you’d usually feel in that kind of moment?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 10 },
    )

    node10_3 = DialogNode(
        id="10_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 10 },
    )


    node10_4 = DialogNode(
        id="10_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 10 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q11 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node11_0 = DialogNode(
        id="11_0",
        text="In everyday situations—like waiting in line, sitting next to someone, or meeting new people—some enjoy making small talk, while others find it uncomfortable or unnecessary.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 11 },
    )

    node11_1 = DialogNode(
        id="11_1",
        text="Can you think of a time when you struck up a casual conversation with someone you didn’t know well, just for the sake of chatting? What was that like for you?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 11 },
    )
    
    node11_2 = DialogNode(
        id="11_2",
        text="If that hasn’t happened recently, how do you usually feel about small talk or light conversation?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 11 },
    )

    node11_3 = DialogNode(
        id="11_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 11 },
    )


    node11_4 = DialogNode(
        id="11_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 11 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q12 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node12_0 = DialogNode(
        id="12_0",
        text="People vary in how much energy and enthusiasm they bring to daily life. Some tend to feel upbeat and energized, while others are more low-key or subdued most of the time. Think about a typical weekday—whether it’s for work, study, or other responsibilities. ",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 12 },
    )

    node12_1 = DialogNode(
        id="12_1",
        text="As you go through your day, how would you describe your usual emotional tone and energy level? Can you recall a recent day when you especially noticed feeling either energized or drained? What was going on that day?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 12 },
    )
    
    node12_2 = DialogNode(
        id="12_2",
        text="If no specific day comes to mind, how would you generally describe your mood and energy across an average week?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 12 },
    )

    node12_3 = DialogNode(
        id="12_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 12 },
    )


    node12_4 = DialogNode(
        id="12_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 12 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q13 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node13_0 = DialogNode(
        id="13_0",
        text="Sometimes we’re hurt or mistreated by people we know—like a friend letting us down, a colleague taking credit, or someone speaking behind our back.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 13 },
    )

    node13_1 = DialogNode(
        id="13_1",
        text="Can you think of a time when someone treated you unfairly or hurt your trust? How did you feel at the time, and were you eventually able to forgive or rebuild the relationship?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 13 },
    )
    
    node13_2 = DialogNode(
        id="13_2",
        text="If you haven't experienced something like this, how do you think you'd respond?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 13 },
    )

    node13_3 = DialogNode(
        id="13_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 13 },
    )


    node13_4 = DialogNode(
        id="13_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 13 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q14 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node14_0 = DialogNode(
        id="14_0",
        text="In everyday interactions, people often have to respond to others' mistakes or shortcomings. Think of a time when you noticed a mistake or flaw in someone’s behavior or work.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 14 },
    )

    node14_1 = DialogNode(
        id="14_1",
        text="What were you thinking about it? How did you feel—did you feel critical, or were you inclined to be understanding? How did you actually respond—did you react with a gentle, accepting approach, or did you express criticism or harshness?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 14 },
    )
    
    node14_2 = DialogNode(
        id="14_2",
        text="If you can’t recall a situation like this, how do you think you’d typically respond?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 14 },
    )

    node14_3 = DialogNode(
        id="14_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 14 },
    )


    node14_4 = DialogNode(
        id="14_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 14 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q15 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node15_0 = DialogNode(
        id="15_0",
        text="Sometimes in conversations—at work, school, or in daily life—someone strongly disagrees with our opinion or challenges how we see things.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 15 },
    )

    node15_1 = DialogNode(
        id="15_1",
        text="Can you think of a time when that happened? What were you thinking and feeling in that moment? How did you respond—did you stick to your original view, adjust your stance, or try to find a middle ground?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 15 },
    )
    
    node15_2 = DialogNode(
        id="15_2",
        text="If nothing comes to mind, how do you think you'd typically react in that kind of situation?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 15 },
    )

    node15_3 = DialogNode(
        id="15_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 15 },
    )


    node15_4 = DialogNode(
        id="15_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 15 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q16 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node16_0 = DialogNode(
        id="16_0",
        text="In daily life, we sometimes face delays or situations that don’t go as planned—like waiting in a long line, a late appointment, or traffic jams.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 16 },
    )

    node16_1 = DialogNode(
        id="16_1",
        text="Think of a time when you were in a situation like that. What went through your mind? How did you feel in that moment? And what did you actually do—did you stay calm or react in some way?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 16 },
    )
    
    node16_2 = DialogNode(
        id="16_2",
        text="If you can’t think of a situation like this, how do you think you’d usually react?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 16 },
    )

    node16_3 = DialogNode(
        id="16_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 16 },
    )


    node16_4 = DialogNode(
        id="16_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 16 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q17 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node17_0 = DialogNode(
        id="17_0",
        text="Some people like to return things to their proper place right after using them—others leave things out and organize later.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 17 },
    )

    node17_1 = DialogNode(
        id="17_1",
        text="Can you describe how you typically handle your personal belongings, like notebooks, clothes, bags, or supplies, during a normal day or week? How do you feel when things aren’t where they belong?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 17 },
    )
    
    node17_2 = DialogNode(
        id="17_2",
        text="If no specific example comes to mind, how would someone close to you describe your typical level of tidiness?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 17 },
    )

    node17_3 = DialogNode(
        id="17_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 17 },
    )


    node17_4 = DialogNode(
        id="17_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 17 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q18 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node18_0 = DialogNode(
        id="18_0",
        text="Some people consistently push themselves to do more than what’s required, even when no one is checking. Others prefer to do just what’s needed and move on.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 18 },
    )

    node18_1 = DialogNode(
        id="18_1",
        text="Can you think of a time when you had a task or goal to complete—like a paper, job, or project—and you had to decide how much effort to put in? What was your mindset, and how much effort did you actually give?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 18 },
    )
    
    node18_2 = DialogNode(
        id="18_2",
        text="If no clear example comes to mind, how do you usually approach effort when no one is watching or enforcing it?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 18 },
    )

    node18_3 = DialogNode(
        id="18_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 18 },
    )


    node18_4 = DialogNode(
        id="18_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 18 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q19 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node19_0 = DialogNode(
        id="19_0",
        text="When you’re close to finishing a task—like writing, preparing something for work or school, or submitting an assignment—people vary in how much attention they give to polishing or checking for small mistakes.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 19 },
    )

    node19_1 = DialogNode(
        id="19_1",
        text="Can you think of a time when you were wrapping something up and had to decide whether or not to go back and review it further? What was going through your mind, and what did you choose to do?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 19 },
    )
    
    node19_2 = DialogNode(
        id="19_2",
        text="Can you think of a time when you were wrapping something up and had to decide whether or not to go back and review it further? What was going through your mind, and what did you choose to do? If no example comes to mind, how do you usually approach the final stage of your work?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 19 },
    )

    node19_3 = DialogNode(
        id="19_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 19 },
    )


    node19_4 = DialogNode(
        id="19_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 19 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q20 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node20_0 = DialogNode(
        id="20_0",
        text="Sometimes, situations arise that might trigger a strong emotional response—such as feeling provoked, pressured, or taken by surprise.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 20 },
    )

    node20_1 = DialogNode(
        id="20_1",
        text="Can you recall a specific instance when this happened? In that moment, did you pause to think things through, or did you act quickly? What were your immediate thoughts or impulses? How did you feel at the time? What did you actually do, and how did you feel afterward about the way you handled it?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 20 },
    )
    
    node20_2 = DialogNode(
        id="20_2",
        text="Can you recall a specific instance when this happened? In that moment, did you pause to think things through, or did you act quickly? What were your immediate thoughts or impulses? How did you feel at the time? What did you actually do, and how did you feel afterward about the way you handled it? If you can’t recall a specific instance, how do you think you would typically respond in such a situation?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 20 },
    )

    node20_3 = DialogNode(
        id="20_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 20 },
    )


    node20_4 = DialogNode(
        id="20_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 20 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q21 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node21_0 = DialogNode(
        id="21_0",
        text="Sometimes we spend time in places where the natural surroundings stand out—like a hike, a park, or a scenic view.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 21 },
    )

    node21_1 = DialogNode(
        id="21_1",
        text="Can you recall a time when you were in a natural setting like that? Did you notice anything that caught your attention? What were your thoughts about it? How did it make you feel? How did you respond—did you stop to take it in, talk about it, take a photo, or move on without much notice? ",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 21 },
    )
    
    node21_2 = DialogNode(
        id="21_2",
        text="Can you recall a time when you were in a natural setting like that? Did you notice anything that caught your attention? What were your thoughts about it? How did it make you feel? How did you respond—did you stop to take it in, talk about it, take a photo, or move on without much notice? If nothing comes to mind, how do you think you’d respond in a natural setting—would you notice and appreciate the scenery, or not feel particularly moved by it?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 21 },
    )

    node21_3 = DialogNode(
        id="21_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 21 },
    )


    node21_4 = DialogNode(
        id="21_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 21 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q22 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node22_0 = DialogNode(
        id="22_0",
        text="Sometimes we come across a topic—maybe in a conversation, something we read, or something online—that catches our attention in some way.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 22 },
    )

    node22_1 = DialogNode(
        id="22_1",
        text="Can you think of a time when that happened to you? What was the topic, and what did you think and feel about it in that moment? Did you want to know more, or did you move on? What did you end up doing, if anything?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 22 },
    )
    
    node22_2 = DialogNode(
        id="22_2",
        text="Can you think of a time when that happened to you? What was the topic, and what did you think and feel about it in that moment? Did you want to know more, or did you move on? What did you end up doing, if anything? If nothing comes to mind, how do you think you'd respond in that kind of situation?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 22 },
    )

    node22_3 = DialogNode(
        id="22_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 22 },
    )


    node22_4 = DialogNode(
        id="22_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 22 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q23 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node23_0 = DialogNode(
        id="23_0",
        text="Sometimes when we’re doing a task—whether at school, at work, or in daily life—we can choose to follow instructions or come up with our own way of doing things.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 23 },
    )

    node23_1 = DialogNode(
        id="23_1",
        text="Can you think of a time when you were in a situation like that? What were you thinking as you approached the task—did you feel interested in doing it your own way, or did the usual method feel more comfortable or effective? How did you feel, and what did you end up doing?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 23 },
    )
    
    node23_2 = DialogNode(
        id="23_2",
        text="Can you think of a time when you were in a situation like that? What were you thinking as you approached the task—did you feel interested in doing it your own way, or did the usual method feel more comfortable or effective? How did you feel, and what did you end up doing? If nothing specific comes to mind, how do you usually approach familiar tasks—do you like to follow standard methods, or try something different when possible?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 23 },
    )

    node23_3 = DialogNode(
        id="23_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
             "DECLINE_CONTINUE": [],
        },
        info={"progress": 23 },
    )


    node23_4 = DialogNode(
        id="23_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 23 },
    )

    


    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Q24 ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node24_0 = DialogNode(
        id="24_0",
        text="Sometimes we encounter ideas that go strongly against mainstream views—like radical political beliefs, unconventional life choices, or strange scientific theories.",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 24 },
    )

    node24_1 = DialogNode(
        id="24_1",
        text="Can you think of a time when someone around you shared a view or idea that struck you as way outside the norm? What was the topic, how did you feel, did you feel curious, skeptical, uncomfortable, or something else? And how did you respond?",
        node_type=NodeType.PLAIN_MESSAGE,
        info={"progress": 24 },
    )
    
    node24_2 = DialogNode(
        id="24_2",
        text="Can you think of a time when someone around you shared a view or idea that struck you as way outside the norm? What was the topic, how did you feel, did you feel curious, skeptical, uncomfortable, or something else? And how did you respond? If nothing specific comes to mind, how do you think you’d typically react when someone expresses something very unconventional?",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_1_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_1_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_1_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 24 },
    )

    node24_3 = DialogNode(
        id="24_3",
        text="Dummy",
        node_type=NodeType.DEFAULT_QUESTION,
        condition_check=lambda chatting_messages : detect(chatting_messages),
        summary_generators={
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
        },
        parallism_works={
            "NEEDS_CLARIFICATION" : [generate_follow_up_question_2_NEEDS_CLARIFICATION],
            "NONSENSE": [generate_follow_up_question_2_NONSENSE],
            "UNINFORMATIVE": [generate_follow_up_question_2_UNINFORMATIVE],
            "VALID": [],
            "DECLINE_CONTINUE": [],
        },
        info={"progress": 24 },
    )


    node24_4 = DialogNode(
        id="24_4",
        text="Dummy",
        node_type=NodeType.NO_CONDITION_CHECK,
        summary_generators={
            "default": lambda chatting_messages : say_thank_you_and_go_next(chatting_messages),
        },
        info={"progress": 24 },
    )

    


    
    # ---------------------------------------------------------------------------- #
    # ------------------------------------ Qlast ------------------------------------ #
    # ---------------------------------------------------------------------------- #
    node_ending = DialogNode(
        id="-1",
        text=lambda user_name: f"Goodbye, {user_name}, have a good day!",
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
    node0_7.add_next_node("default", node1_0)


   # ------------------------- 1 -------------------------------
    node1_0.add_next_node("default", node1_1)
    node1_1.add_next_node("default", node1_2)

    node1_2.add_next_node("NEEDS_CLARIFICATION", node1_3)
    node1_2.add_next_node("NONSENSE", node1_3)
    node1_2.add_next_node("UNINFORMATIVE", node1_3)
    node1_2.add_next_node("VALID", node2_0)
    node1_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node1_3.add_next_node("NEEDS_CLARIFICATION", node1_4)
    node1_3.add_next_node("NONSENSE", node1_4)
    node1_3.add_next_node("UNINFORMATIVE", node1_4)
    node1_3.add_next_node("VALID", node2_0)
    node1_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node1_4.add_next_node("default", node2_0)
    

    

    # ------------------------- 2 -------------------------------
    node2_0.add_next_node("default", node2_1)
    node2_1.add_next_node("default", node2_2)

    node2_2.add_next_node("NEEDS_CLARIFICATION", node2_3)
    node2_2.add_next_node("NONSENSE", node2_3)
    node2_2.add_next_node("UNINFORMATIVE", node2_3)
    node2_2.add_next_node("VALID", node3_0)
    node2_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node2_3.add_next_node("NEEDS_CLARIFICATION", node2_4)
    node2_3.add_next_node("NONSENSE", node2_4)
    node2_3.add_next_node("UNINFORMATIVE", node2_4)
    node2_3.add_next_node("VALID", node3_0)
    node2_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node2_4.add_next_node("default", node3_0)
    

    

    # ------------------------- 3 -------------------------------
    node3_0.add_next_node("default", node3_1)
    node3_1.add_next_node("default", node3_2)

    node3_2.add_next_node("NEEDS_CLARIFICATION", node3_3)
    node3_2.add_next_node("NONSENSE", node3_3)
    node3_2.add_next_node("UNINFORMATIVE", node3_3)
    node3_2.add_next_node("VALID", node4_0)
    node3_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node3_3.add_next_node("NEEDS_CLARIFICATION", node3_4)
    node3_3.add_next_node("NONSENSE", node3_4)
    node3_3.add_next_node("UNINFORMATIVE", node3_4)
    node3_3.add_next_node("VALID", node4_0)
    node3_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node3_4.add_next_node("default", node4_0)
    

    

    # ------------------------- 4 -------------------------------
    node4_0.add_next_node("default", node4_1)
    node4_1.add_next_node("default", node4_2)

    node4_2.add_next_node("NEEDS_CLARIFICATION", node4_3)
    node4_2.add_next_node("NONSENSE", node4_3)
    node4_2.add_next_node("UNINFORMATIVE", node4_3)
    node4_2.add_next_node("VALID", node5_0)
    node4_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node4_3.add_next_node("NEEDS_CLARIFICATION", node4_4)
    node4_3.add_next_node("NONSENSE", node4_4)
    node4_3.add_next_node("UNINFORMATIVE", node4_4)
    node4_3.add_next_node("VALID", node5_0)
    node4_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node4_4.add_next_node("default", node5_0)
    

    

    # ------------------------- 5 -------------------------------
    node5_0.add_next_node("default", node5_1)
    node5_1.add_next_node("default", node5_2)

    node5_2.add_next_node("NEEDS_CLARIFICATION", node5_3)
    node5_2.add_next_node("NONSENSE", node5_3)
    node5_2.add_next_node("UNINFORMATIVE", node5_3)
    node5_2.add_next_node("VALID", node6_0)
    node5_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node5_3.add_next_node("NEEDS_CLARIFICATION", node5_4)
    node5_3.add_next_node("NONSENSE", node5_4)
    node5_3.add_next_node("UNINFORMATIVE", node5_4)
    node5_3.add_next_node("VALID", node6_0)
    node5_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node5_4.add_next_node("default", node6_0)
    

    

    # ------------------------- 6 -------------------------------
    node6_0.add_next_node("default", node6_1)
    node6_1.add_next_node("default", node6_2)

    node6_2.add_next_node("NEEDS_CLARIFICATION", node6_3)
    node6_2.add_next_node("NONSENSE", node6_3)
    node6_2.add_next_node("UNINFORMATIVE", node6_3)
    node6_2.add_next_node("VALID", node7_0)
    node6_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node6_3.add_next_node("NEEDS_CLARIFICATION", node6_4)
    node6_3.add_next_node("NONSENSE", node6_4)
    node6_3.add_next_node("UNINFORMATIVE", node6_4)
    node6_3.add_next_node("VALID", node7_0)
    node6_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node6_4.add_next_node("default", node7_0)
    

    

    # ------------------------- 7 -------------------------------
    node7_0.add_next_node("default", node7_1)
    node7_1.add_next_node("default", node7_2)

    node7_2.add_next_node("NEEDS_CLARIFICATION", node7_3)
    node7_2.add_next_node("NONSENSE", node7_3)
    node7_2.add_next_node("UNINFORMATIVE", node7_3)
    node7_2.add_next_node("VALID", node8_0)
    node7_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node7_3.add_next_node("NEEDS_CLARIFICATION", node7_4)
    node7_3.add_next_node("NONSENSE", node7_4)
    node7_3.add_next_node("UNINFORMATIVE", node7_4)
    node7_3.add_next_node("VALID", node8_0)
    node7_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node7_4.add_next_node("default", node8_0)
    

    

    # ------------------------- 8 -------------------------------
    node8_0.add_next_node("default", node8_1)
    node8_1.add_next_node("default", node8_2)

    node8_2.add_next_node("NEEDS_CLARIFICATION", node8_3)
    node8_2.add_next_node("NONSENSE", node8_3)
    node8_2.add_next_node("UNINFORMATIVE", node8_3)
    node8_2.add_next_node("VALID", node9_0)
    node8_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node8_3.add_next_node("NEEDS_CLARIFICATION", node8_4)
    node8_3.add_next_node("NONSENSE", node8_4)
    node8_3.add_next_node("UNINFORMATIVE", node8_4)
    node8_3.add_next_node("VALID", node9_0)
    node8_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node8_4.add_next_node("default", node9_0)
    

    

    # ------------------------- 9 -------------------------------
    node9_0.add_next_node("default", node9_1)
    node9_1.add_next_node("default", node9_2)

    node9_2.add_next_node("NEEDS_CLARIFICATION", node9_3)
    node9_2.add_next_node("NONSENSE", node9_3)
    node9_2.add_next_node("UNINFORMATIVE", node9_3)
    node9_2.add_next_node("VALID", node10_0)
    node9_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node9_3.add_next_node("NEEDS_CLARIFICATION", node9_4)
    node9_3.add_next_node("NONSENSE", node9_4)
    node9_3.add_next_node("UNINFORMATIVE", node9_4)
    node9_3.add_next_node("VALID", node10_0)
    node9_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node9_4.add_next_node("default", node10_0)
    

    

    # ------------------------- 10 -------------------------------
    node10_0.add_next_node("default", node10_1)
    node10_1.add_next_node("default", node10_2)

    node10_2.add_next_node("NEEDS_CLARIFICATION", node10_3)
    node10_2.add_next_node("NONSENSE", node10_3)
    node10_2.add_next_node("UNINFORMATIVE", node10_3)
    node10_2.add_next_node("VALID", node11_0)
    node10_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node10_3.add_next_node("NEEDS_CLARIFICATION", node10_4)
    node10_3.add_next_node("NONSENSE", node10_4)
    node10_3.add_next_node("UNINFORMATIVE", node10_4)
    node10_3.add_next_node("VALID", node11_0)
    node10_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node10_4.add_next_node("default", node11_0)
    

    

    # ------------------------- 11 -------------------------------
    node11_0.add_next_node("default", node11_1)
    node11_1.add_next_node("default", node11_2)

    node11_2.add_next_node("NEEDS_CLARIFICATION", node11_3)
    node11_2.add_next_node("NONSENSE", node11_3)
    node11_2.add_next_node("UNINFORMATIVE", node11_3)
    node11_2.add_next_node("VALID", node12_0)
    node11_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node11_3.add_next_node("NEEDS_CLARIFICATION", node11_4)
    node11_3.add_next_node("NONSENSE", node11_4)
    node11_3.add_next_node("UNINFORMATIVE", node11_4)
    node11_3.add_next_node("VALID", node12_0)
    node11_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node11_4.add_next_node("default", node12_0)
    

    

    # ------------------------- 12 -------------------------------
    node12_0.add_next_node("default", node12_1)
    node12_1.add_next_node("default", node12_2)

    node12_2.add_next_node("NEEDS_CLARIFICATION", node12_3)
    node12_2.add_next_node("NONSENSE", node12_3)
    node12_2.add_next_node("UNINFORMATIVE", node12_3)
    node12_2.add_next_node("VALID", node13_0)
    node12_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node12_3.add_next_node("NEEDS_CLARIFICATION", node12_4)
    node12_3.add_next_node("NONSENSE", node12_4)
    node12_3.add_next_node("UNINFORMATIVE", node12_4)
    node12_3.add_next_node("VALID", node13_0)
    node12_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node12_4.add_next_node("default", node13_0)
    

    

    # ------------------------- 13 -------------------------------
    node13_0.add_next_node("default", node13_1)
    node13_1.add_next_node("default", node13_2)

    node13_2.add_next_node("NEEDS_CLARIFICATION", node13_3)
    node13_2.add_next_node("NONSENSE", node13_3)
    node13_2.add_next_node("UNINFORMATIVE", node13_3)
    node13_2.add_next_node("VALID", node14_0)
    node13_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node13_3.add_next_node("NEEDS_CLARIFICATION", node13_4)
    node13_3.add_next_node("NONSENSE", node13_4)
    node13_3.add_next_node("UNINFORMATIVE", node13_4)
    node13_3.add_next_node("VALID", node14_0)
    node13_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node13_4.add_next_node("default", node14_0)
    

    

    # ------------------------- 14 -------------------------------
    node14_0.add_next_node("default", node14_1)
    node14_1.add_next_node("default", node14_2)

    node14_2.add_next_node("NEEDS_CLARIFICATION", node14_3)
    node14_2.add_next_node("NONSENSE", node14_3)
    node14_2.add_next_node("UNINFORMATIVE", node14_3)
    node14_2.add_next_node("VALID", node15_0)
    node14_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node14_3.add_next_node("NEEDS_CLARIFICATION", node14_4)
    node14_3.add_next_node("NONSENSE", node14_4)
    node14_3.add_next_node("UNINFORMATIVE", node14_4)
    node14_3.add_next_node("VALID", node15_0)
    node14_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node14_4.add_next_node("default", node15_0)
    

    

    # ------------------------- 15 -------------------------------
    node15_0.add_next_node("default", node15_1)
    node15_1.add_next_node("default", node15_2)

    node15_2.add_next_node("NEEDS_CLARIFICATION", node15_3)
    node15_2.add_next_node("NONSENSE", node15_3)
    node15_2.add_next_node("UNINFORMATIVE", node15_3)
    node15_2.add_next_node("VALID", node16_0)
    node15_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node15_3.add_next_node("NEEDS_CLARIFICATION", node15_4)
    node15_3.add_next_node("NONSENSE", node15_4)
    node15_3.add_next_node("UNINFORMATIVE", node15_4)
    node15_3.add_next_node("VALID", node16_0)
    node15_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node15_4.add_next_node("default", node16_0)
    

    

    # ------------------------- 16 -------------------------------
    node16_0.add_next_node("default", node16_1)
    node16_1.add_next_node("default", node16_2)

    node16_2.add_next_node("NEEDS_CLARIFICATION", node16_3)
    node16_2.add_next_node("NONSENSE", node16_3)
    node16_2.add_next_node("UNINFORMATIVE", node16_3)
    node16_2.add_next_node("VALID", node17_0)
    node16_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node16_3.add_next_node("NEEDS_CLARIFICATION", node16_4)
    node16_3.add_next_node("NONSENSE", node16_4)
    node16_3.add_next_node("UNINFORMATIVE", node16_4)
    node16_3.add_next_node("VALID", node17_0)
    node16_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node16_4.add_next_node("default", node17_0)
    

    

    # ------------------------- 17 -------------------------------
    node17_0.add_next_node("default", node17_1)
    node17_1.add_next_node("default", node17_2)

    node17_2.add_next_node("NEEDS_CLARIFICATION", node17_3)
    node17_2.add_next_node("NONSENSE", node17_3)
    node17_2.add_next_node("UNINFORMATIVE", node17_3)
    node17_2.add_next_node("VALID", node18_0)
    node17_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node17_3.add_next_node("NEEDS_CLARIFICATION", node17_4)
    node17_3.add_next_node("NONSENSE", node17_4)
    node17_3.add_next_node("UNINFORMATIVE", node17_4)
    node17_3.add_next_node("VALID", node18_0)
    node17_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node17_4.add_next_node("default", node18_0)
    

    

    # ------------------------- 18 -------------------------------
    node18_0.add_next_node("default", node18_1)
    node18_1.add_next_node("default", node18_2)

    node18_2.add_next_node("NEEDS_CLARIFICATION", node18_3)
    node18_2.add_next_node("NONSENSE", node18_3)
    node18_2.add_next_node("UNINFORMATIVE", node18_3)
    node18_2.add_next_node("VALID", node19_0)
    node18_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node18_3.add_next_node("NEEDS_CLARIFICATION", node18_4)
    node18_3.add_next_node("NONSENSE", node18_4)
    node18_3.add_next_node("UNINFORMATIVE", node18_4)
    node18_3.add_next_node("VALID", node19_0)
    node18_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node18_4.add_next_node("default", node19_0)
    

    

    # ------------------------- 19 -------------------------------
    node19_0.add_next_node("default", node19_1)
    node19_1.add_next_node("default", node19_2)

    node19_2.add_next_node("NEEDS_CLARIFICATION", node19_3)
    node19_2.add_next_node("NONSENSE", node19_3)
    node19_2.add_next_node("UNINFORMATIVE", node19_3)
    node19_2.add_next_node("VALID", node20_0)
    node19_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node19_3.add_next_node("NEEDS_CLARIFICATION", node19_4)
    node19_3.add_next_node("NONSENSE", node19_4)
    node19_3.add_next_node("UNINFORMATIVE", node19_4)
    node19_3.add_next_node("VALID", node20_0)
    node19_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node19_4.add_next_node("default", node20_0)
    

    

    # ------------------------- 20 -------------------------------
    node20_0.add_next_node("default", node20_1)
    node20_1.add_next_node("default", node20_2)

    node20_2.add_next_node("NEEDS_CLARIFICATION", node20_3)
    node20_2.add_next_node("NONSENSE", node20_3)
    node20_2.add_next_node("UNINFORMATIVE", node20_3)
    node20_2.add_next_node("VALID", node21_0)
    node20_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node20_3.add_next_node("NEEDS_CLARIFICATION", node20_4)
    node20_3.add_next_node("NONSENSE", node20_4)
    node20_3.add_next_node("UNINFORMATIVE", node20_4)
    node20_3.add_next_node("VALID", node21_0)
    node20_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node20_4.add_next_node("default", node21_0)
    

    

    # ------------------------- 21 -------------------------------
    node21_0.add_next_node("default", node21_1)
    node21_1.add_next_node("default", node21_2)

    node21_2.add_next_node("NEEDS_CLARIFICATION", node21_3)
    node21_2.add_next_node("NONSENSE", node21_3)
    node21_2.add_next_node("UNINFORMATIVE", node21_3)
    node21_2.add_next_node("VALID", node22_0)
    node21_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node21_3.add_next_node("NEEDS_CLARIFICATION", node21_4)
    node21_3.add_next_node("NONSENSE", node21_4)
    node21_3.add_next_node("UNINFORMATIVE", node21_4)
    node21_3.add_next_node("VALID", node22_0)
    node21_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node21_4.add_next_node("default", node22_0)
    

    

    # ------------------------- 22 -------------------------------
    node22_0.add_next_node("default", node22_1)
    node22_1.add_next_node("default", node22_2)

    node22_2.add_next_node("NEEDS_CLARIFICATION", node22_3)
    node22_2.add_next_node("NONSENSE", node22_3)
    node22_2.add_next_node("UNINFORMATIVE", node22_3)
    node22_2.add_next_node("VALID", node23_0)
    node22_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node22_3.add_next_node("NEEDS_CLARIFICATION", node22_4)
    node22_3.add_next_node("NONSENSE", node22_4)
    node22_3.add_next_node("UNINFORMATIVE", node22_4)
    node22_3.add_next_node("VALID", node23_0)
    node22_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node22_4.add_next_node("default", node23_0)
    

    

    # ------------------------- 23 -------------------------------
    node23_0.add_next_node("default", node23_1)
    node23_1.add_next_node("default", node23_2)

    node23_2.add_next_node("NEEDS_CLARIFICATION", node23_3)
    node23_2.add_next_node("NONSENSE", node23_3)
    node23_2.add_next_node("UNINFORMATIVE", node23_3)
    node23_2.add_next_node("VALID", node24_0)
    node23_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node23_3.add_next_node("NEEDS_CLARIFICATION", node23_4)
    node23_3.add_next_node("NONSENSE", node23_4)
    node23_3.add_next_node("UNINFORMATIVE", node23_4)
    node23_3.add_next_node("VALID", node24_0)
    node23_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node23_4.add_next_node("default", node24_0)
    

    

    # ------------------------- 24 -------------------------------
    node24_0.add_next_node("default", node24_1)
    node24_1.add_next_node("default", node24_2)

    node24_2.add_next_node("NEEDS_CLARIFICATION", node24_3)
    node24_2.add_next_node("NONSENSE", node24_3)
    node24_2.add_next_node("UNINFORMATIVE", node24_3)
    node24_2.add_next_node("VALID", node_ending)
    node24_2.add_next_node("DECLINE_CONTINUE", node_exiting)

    node24_3.add_next_node("NEEDS_CLARIFICATION", node24_4)
    node24_3.add_next_node("NONSENSE", node24_4)
    node24_3.add_next_node("UNINFORMATIVE", node24_4)
    node24_3.add_next_node("VALID", node_ending)
    node24_3.add_next_node("DECLINE_CONTINUE", node_exiting)

    node24_4.add_next_node("default", node_ending)
    



    # ------------------------ decline ---------------------------
    node_exiting.add_next_node("default", node_exiting_1)
    node_exiting_1.add_next_node("default", node_exiting_2)
    node_exiting_2.add_next_node("default", node_exiting_3)

    return node0_0


