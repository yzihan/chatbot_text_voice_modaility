import random
import re
from typing import Dict, List


SELECTED_QUESTION_WORDING = {
    "F1Q3": "Sometimes people adjust what they say because they want others to like them or think well of them. In general, when someone close to you asks for your honest opinion but you suspect being fully honest might make you less likable or less accepted, how do you usually respond? Do you tend to be straightforward, or adjust your words to keep harmony? If it helps, you can share an example that shows what’s most typical for you.",
    "F2Q2": "There are situations where people can gain an advantage—like a reward, a better grade, or praise—by bending or breaking rules, especially when the risk of getting caught is low. In general, if you face that kind of situation, how do you usually decide what to do? Do you tend to follow the rules, or sometimes consider breaking them? What usually influences your decision? If it helps, you can share an example that reflects what’s most typical for you.",
    "F3Q1": "Sometimes people consider buying something expensive, like luxury clothing, new electronics, or a special experience, even if they don’t really need it. When you face that kind of choice, what usually goes through your mind, and what do you usually decide? If it helps, you can share an example that shows what’s most typical for you.",
    "F4Q3": "In settings like school, work, or team projects, people often contribute at different levels. For instance, you might work especially hard and contribute more than most people in the group. In general, if you feel you clearly outperformed others around you, what are your usual thoughts and feelings in that situation? How do you usually respond if others don’t notice your contribution? Does it typically influence how you see yourself or how you behave afterward? If it helps, you can share an example that reflects what’s most typical for you.",
    "F5Q1": "Sometimes we need to go somewhere despite unsafe or risky conditions—like driving through a snowstorm, walking alone at night, or traveling during a weather alert. In general, if you face that kind of situation, how much fear do you usually feel, and how does it usually affect what you decide to do? If it helps, you can share an example that shows what’s most typical for you.",
    "F6Q1": "Waiting to hear back about something important—like an application, a decision, or news—can make some people anxious. In general, if you are waiting for an outcome and aren’t sure what will happen, what thoughts and feelings do you usually have, and how does it affect what you do? If it helps, you can share an example that shows what’s most typical for you.",
    "F7Q2": "Sometimes when people feel anxious or worried, they immediately talk to someone they trust, while others keep it to themselves. If you are feeling anxious or worried, how do you usually respond—do you tend to share it or keep it private? How does that choice usually affect how you feel afterward? Could you share an example that reflects your typical response.",
    "F8Q3": "Events like weddings, reunions, or even reflecting on old photos can bring up strong feelings for some people, while others stay more neutral. If you are in a symbolic or nostalgic moment with people you care about, how do you usually feel—do you become strongly moved, or stay more neutral? How does it typically affect your sense of closeness or attachment to others? You can share an example that shows how you usually react in those situations.",
    "F9Q2": "After social events—like a conversation, party, or class discussion—some people reflect on how they came across, while others don’t think much about it. When you’ve just been in a group interaction, how often do you think about how you came across to others? How does that usually make you feel about yourself, and does it affect what you say or do afterward? You can share an example that shows how you usually respond.",
    "F10Q1": "When meeting someone new—at work, events, or in public—some people start conversations easily, while others feel hesitant. In general, when you meet someone new, how do you usually approach the situation—do you introduce yourself and join in easily, or do you feel more hesitant? How comfortable or nervous do you typically feel, and how does that affect what you do? If you’d like, you can share an example that reflects your usual approach.",
    "F11Q1": "People differ in how much they enjoy casual conversation in everyday situations—like waiting in line, sitting next to someone, or meeting new people. In general, what do you usually do in those situations—do you strike up small talk or prefer to keep to yourself? How do you usually feel about it? If you’d like, you can share an example that reflects what feels most natural for you.",
    "F12Q1": "People vary in how much energy and enthusiasm they bring to daily life. Some tend to feel upbeat and energized, while others are more low-key or subdued most of the time. In general, thinking about your usual routines—whether at work, school, or in daily life—how would you describe your typical mood and energy level? If you’d like, you can share an example that illustrates what feels most typical for you.",
    "F13Q1": "Sometimes people hurt or disappoint us—like a friend letting us down, a colleague taking credit, or someone speaking behind our back. In general, when someone hurts or disappoints you like this, how do you usually respond? Are you more likely to forgive the person and rebuild the relationship, or to hold on to the hurt? What usually influences your decision? If you’d like, you can share an example that reflects what’s most typical for you.",
    "F14Q1": "In everyday interactions, people sometimes make mistakes or fall short. In general, when you notice this, how do you usually react—do you tend to be more critical, or more understanding? What do you typically do in response? If you’d like, you can share an example that shows what feels most typical for you.",
    "F15Q3": "In group decisions—like making plans or agreeing on how to do something—people sometimes have strong preferences for their own way of doing things. In general, when your preference is different from others’, how do you usually respond—do you hold firm to your way, or are you more willing to go along with the group? You might describe a situation that reflects how you usually handle this.",
    "F16Q1": "In daily life, we often face delays or situations that don’t go as planned—like waiting in a long line, a late appointment, or traffic jams. When this happens to you, what usually goes through your mind, how do you feel, and how do you tend to respond—do you stay calm or react in some way? Can you share an example that shows what feels most typical for you?",
    "F17Q1": "Some people like to return things to their proper place right after using them, while others naturally leave things out and tidy up later. And some people might feel comfortable with a bit of clutter or even see it as part of their style. In general, during a normal day or week, how do you usually keep track of and maintain order with your things—like notebooks, clothes, bags, or supplies? How do you feel when items are left out of place for a while? Can you share what feels most typical for you?",
    "F18Q1": "Some people push themselves to do more than required, even when no one is checking, while others do only what’s needed. When you have a task—like a paper, project, or job—how do you usually decide how much effort to put in? What influences your choice, and how much effort do you typically give? If it helps, you can share an example of a time when you had to decide how much effort to put into something.",
    "F19Q3": "In everyday tasks—like writing, formatting, or organizing—people sometimes notice small things that could be improved, such as spacing, punctuation, or alignment. When you notice these kinds of small flaws in your own work, what usually goes through your mind, and how do you usually feel and respond—do you feel a strong need to correct them, or are you comfortable letting small imperfections stay? Feel free to share what reflects your typical style.",
    "F20Q1": "Sometimes situations arise that might trigger a strong emotional response—such as feeling provoked, pressured, or taken by surprise. When situations like these happen, do you usually pause to think things through, or act quickly on your impulses? What kinds of thoughts and feelings typically guide your response in those moments? You might describe a situation that reflects how you usually respond.",
    "F21Q1": "When you’re in a natural setting—like on a hike, in a park, or looking at a scenic view—how do you usually respond? Do you tend to pause and appreciate it, talk about it, take a photo, or move on without much notice? How do those settings typically make you feel? If you’d like, you can share an example that reflects what’s most typical for you.",
    "F22Q2": "People often come across things they don’t fully understand—like a scientific idea, a piece of history, or how something works in daily life. In general, how do you usually react when you find something unfamiliar that catches your attention, such as looking into it, asking questions, or letting it go? If it helps, you can describe an example that reflects your usual response.",
    "F23Q2": "When people face a challenge, some stick with familiar solutions, while others try new approaches. When you face a challenge, how do you usually respond, and what tends to guide that choice? Feel free to share an example if one comes to mind.",
    "F24Q3": "In conversations or media, we sometimes come across viewpoints or practices that challenge traditional norms or beliefs. How do you usually react when something like that happens? Do you feel open, curious, resistant, offended, or indifferent? What thoughts or emotions typically come up, and how do you tend to respond—by discussing, researching, or letting it go? If it helps, you can share an example that shows what’s most typical for you.",
}

SELECTED_QUESTION_INDICES = list(SELECTED_QUESTION_WORDING.keys())


def get_randomized_selected_question_indices() -> List[str]:
    question_indices = SELECTED_QUESTION_INDICES.copy()
    random.shuffle(question_indices)
    return question_indices


def apply_selected_question_wording(node_mappings: Dict) -> None:
    missing = sorted(set(SELECTED_QUESTION_INDICES) - set(node_mappings))
    if missing:
        raise ValueError(f"Selected questions are missing from node mappings: {missing}")

    for question_index, final_wording in SELECTED_QUESTION_WORDING.items():
        intro, prompt = split_question_for_chat(final_wording)
        nodes = node_mappings[question_index]
        nodes[0].text = intro
        nodes[1].text = ""
        nodes[2].text = prompt
        nodes[0].info["question_index"] = question_index
        nodes[1].info["question_index"] = question_index
        nodes[2].info["question_index"] = question_index


def split_question_for_chat(text: str) -> tuple[str, str]:
    normalized = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    if len(sentences) <= 1:
        return normalized, normalized

    return " ".join(sentences[:-1]), sentences[-1]
