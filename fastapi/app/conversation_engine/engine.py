from __future__ import annotations

import os
from typing import List, Dict, Any, Callable, Optional, Union
from .node import DialogNode, NodeType, SelectionOption, Message, NodeQuestion, Signal
import pickle
import copy
from .openai_api import send_messages
from .utils import parse_to_json
from .logger import logger
from .question_list.codes.question_list import create_quetion_nodes
from datetime import datetime
import random

import uuid


def utc_timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="microseconds") + "Z"


def assistant_message(content: str, info: Optional[Dict] = None) -> Dict:
    message = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": content,
        "created_at": utc_timestamp(),
    }
    if info is not None:
        message["info"] = info
    return message



def node_question_wrapper(text: NodeQuestion, user_name: str):
    if isinstance(text, str):
        return text
    else:
        return text(user_name)



def get_question_code(user_index: int) -> str:
    """
    return "HEA_2" => ./question_list/codes/HEA_2.txt
    
    """
    N = 1667
    groups = ["HEX", "EXA", "XAC", "ACO", "COH", "OHE"]

    mod = user_index%6
    return groups[mod]


class ConversationEngine:
    def __init__(self, session_id, user_index:int, group: str, source: str, question_indices: List[str], user_info: Dict, root_node: DialogNode, save_path: str = 'conversation_state.txt', selection_reason: str = ""):
        self.session_id = session_id
        self.user_index = user_index
        self.question_code = "HEX"
        self.group = group
        self.source = source
        self.selection_reason = selection_reason
        self.question_indices = question_indices # ["F1Q", "F", ....]

        self.user_info: str = user_info
        self.root_node = root_node
        self.current_node = root_node

        self.complete_chatting_messages: List[Message] = []
        self.node_history: List[DialogNode] = [root_node]

        self.clarification_count = 1000
        self.current_others_option = None
        
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True) # Create directory if not exists

        self._created_time = datetime.utcnow().isoformat()
        self._questions_finished = 0
        self._user_responses_received = 0
        

    def save_conversation_state(self):
        """Save conversation state to a file"""
        try:
            os.makedirs(self.save_path, exist_ok=True)
            metadata = {
                "session_id":  self.session_id,
                "user_index": self.user_index,
                "question_code": self.question_code,
                "group": self.group,
                "selection_reason": self.selection_reason,
                "source": self.source,
                "question_indices": self.question_indices,
                "questions_answered": self._user_responses_received,
                "created_time": self._created_time,
                "updated_time": datetime.utcnow().isoformat(),
            }
            state = {
                'session_id': self.session_id,
                "user_index": self.user_index,
                "question_code": self.question_code,
                "group": self.group,
                "selection_reason": self.selection_reason,
                "source": self.source,
                "question_indices": self.question_indices,
                "user_responses_received": self._user_responses_received,
                "root_node": self.root_node.id,
                'current_node': self.current_node.id,
                # 'node_history': self.node_history,
                "complete_chatting_messages": self.complete_chatting_messages,
                "save_path" : self.save_path
            }
            
            with open(os.path.join(self.save_path, f'{self.session_id}_state.pkl'), 'wb') as f:
                pickle.dump(state, f)
            
            with open(os.path.join(self.save_path, f'metadata.pkl'), 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Conversation state saved for session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to save conversation state: {e}")


    @staticmethod
    def load_conversation_state(session_id: str, save_path: str, user_info: Dict):
        """
        Loads a ConversationEngine instance from saved state.

        Args:
            session_id: ID of the session to load
            save_path: directory where state is saved
            user_info: user info to re-init engine

        Returns:
            ConversationEngine instance or None on failure
        """
        try:
            file_path = os.path.join(save_path, f'{session_id}_state.pkl')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No saved state found for session {session_id}")
            with open(file_path, 'rb') as f:
                state = pickle.load(f)


            metadata_file_path =  os.path.join(save_path, f'metadata.pkl')
            if not os.path.exists(metadata_file_path):
                raise FileNotFoundError(f"No saved meta data found for session {session_id}")
            with open(metadata_file_path, 'rb') as f:
                metadata = pickle.load(f)


            # Create a new tree
            if "question_indices" not in state:
                raise ValueError("History data lost... Please try creating a new chat.")
            root_node = create_quetion_nodes(state["question_indices"])

            def find_node_by_id(node_id):
                def _search(current_node):
                    if current_node.id == node_id:
                        return current_node
                    for option in getattr(current_node, 'options', []):
                        if option.next_node and option.next_node.id == node_id:
                            return option.next_node
                    for next_node in getattr(current_node, 'next_nodes', {}).values():
                        result = _search(next_node)
                        if result:
                            return result
                    return None
                return _search(root_node)

            # Reconstruct state
            engine = ConversationEngine(
                session_id=state["session_id"],
                user_index=state["user_index"],
                group=state.get("group"),
                source=state.get("source"),
                selection_reason=state.get("selection_reason", ""),
                question_indices=state["question_indices"],
                user_info=user_info,
                root_node=root_node,
                save_path=state.get("save_path", save_path)
            )

            engine.current_node = find_node_by_id(state["current_node"])
            engine.question_code = state.get("question_code", "")
            engine.group = state.get("group", "")
            engine.source = state.get("source", "")
            engine.selection_reason = state.get("selection_reason", "")

            engine.node_history = [find_node_by_id(nid) for nid in state.get("node_history", [])]
            engine.complete_chatting_messages = state.get("complete_chatting_messages", [])
            engine._created_time = metadata.get("created_time", datetime.utcnow().isoformat())
            engine._questions_finished = metadata.get("questions_answered", 1)
            engine._user_responses_received = state.get(
                "user_responses_received",
                sum(
                    1
                    for message in engine.complete_chatting_messages
                    if message.get("role") == "user"
                ),
            )
            
            return engine

        except Exception as e:
            logger.error(f"Failed to load conversation state for session {session_id}: {e}")
            return None

        


    def init_conversation(self) -> Dict:
        """
        Main function for first question.
            1. add node.text to chatting_messages and complete chatting_messages
            2. return all the messages from assistant users will see in the first place
        """
        try:

            messages_to_returned = []

            # first message
            msg = assistant_message(
                node_question_wrapper(
                    self.current_node.text,
                    self.user_info["user_name"],
                )
            )
            messages_to_returned.append(msg)
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)


            # move to the next question
            infinite_loop_prevention_cnt = 0
            while self.current_node.eof and self.current_node.node_type != NodeType.END_NODE and infinite_loop_prevention_cnt < 10:
                
                self._move_to_next_node(messages_to_returned)
                infinite_loop_prevention_cnt += 1
            
            if infinite_loop_prevention_cnt >= 10:
                raise Exception(F"Infinite loop created!")


            return {
                "status": "success",
                "messages_to_returned": messages_to_returned,
                "is_ending": self.current_node.node_type == NodeType.END_NODE
            }
        
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {
                "status": "error",
                "error_message": "Some error happend!",
                "error": str(e)
            }

    def load_history_chat(self):
        return {
                "status": "success",
                "messages_to_returned": self.complete_chatting_messages,
                "is_ending": self.current_node.node_type == NodeType.END_NODE
            }
    

    async def process_user_response(
        self,
        user_input: str,
        audioFilepPath: str,
        audio_recording_ids: list[str],
        audio_file_paths: list[str],
        server_message_id: str,
        client_message_id: str,
        client_created_at: Optional[str],
        input_method: str,
        server_received_at: str,
        response_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Main function for all question except first one.
            1. add user/resp and node.text to chatting_messages and complete chatting_messages
            2. return all the messages from assistant following previous usr response
        """

        # Log conversation context
        logger.info(f"Session {self.session_id}: Processing user input")
            
                  
        try:
            messages_to_returned = []
            # user  message
            msg = {
                "id": server_message_id,
                "role": "user",
                "content": user_input,
                "raw_user_input": user_input,
                "audio_file_path": audioFilepPath,
                "audio_file_paths": audio_file_paths,
                "audio_recording_ids": audio_recording_ids,
                "client_message_id": client_message_id,
                "client_created_at": client_created_at,
                "input_method": input_method,
                "created_at": server_received_at,
                "info": response_metadata or copy.deepcopy(self.current_node.info),
            }
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)

            # Handle different node types
            if self.current_node.node_type == NodeType.SELECTION_QUESTION:
                condition = self.handle_selection_question(messages_to_returned)
            elif self.current_node.node_type == NodeType.PLAIN_MESSAGE:
                condition = self.handle_plain_message_question(messages_to_returned)
            elif self.current_node.node_type == NodeType.NO_CONDITION_CHECK:
                condition = self.handle_no_condition_check_question(messages_to_returned)
            elif self.current_node.node_type == NodeType.DEFAULT_QUESTION:
                condition = self.handle_default_question(messages_to_returned)
            elif self.current_node.node_type == NodeType.END_NODE:
                condition = self.handle_end_question(messages_to_returned)
            else:
                raise ValueError("Question type not valid!")
            

            # move to the next question
            infinite_loop_prevention_cnt = 0
            while self.current_node.eof and self.current_node.node_type != NodeType.END_NODE and infinite_loop_prevention_cnt < 10:
                condition = self._move_to_next_node(messages_to_returned, condition=condition)
                infinite_loop_prevention_cnt += 1
            
            if infinite_loop_prevention_cnt >= 10:
                raise Exception(F"Infinite loop created!")

            self._user_responses_received += 1
            
            return {
                "status": "success",
                "messages_to_returned": messages_to_returned,
                "user_message": msg,
                "is_ending": self.current_node.node_type == NodeType.END_NODE
            }
        
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {
                "status": "error",
                "error_message": "Some error happend!",
                "error": str(e)
            }
        
    

    def _ask_for_question_details(self, complete_chatting_messages):
        messages = copy.deepcopy(complete_chatting_messages)
        messages.append({"role":"system", "content": """The above user response is not clearly answer the question. Return a response to ask more details such as "Can you give me more details?", "Could you please give me an clear answer?", etc. Return in the following Pyton Dict format: {{"question": str}} """})
        resp = send_messages(messages=messages, model="gpt-4o-mini")
        

        try:
            resp = parse_to_json(resp)
            return resp["question"]

        except Exception as e:
            try:
                resp = send_messages(messages=messages, model="gpt-4o-mini")
                resp = parse_to_json(resp)
                return resp["question"]

            except Exception as e:
                raise SystemError("Error parsing openai resp")


    #################################################################################
    # handle question funcitons
    #################################################################################
    def handle_default_question(self, messages_to_returned) -> str:
        """
        After receiving user response, it needs to perform
            1. condition check
                for loop <= current_node.max_clarification_attempts if condition == "NA" (not a valid answer), else condition = "default"
    
            2. run parallism_works to condition
            3. run summary generator according to condition
            4. return summary
            5. update eof
        """
        logger.info(f"=========   Session {self.session_id}: Processing input Default Question =========")
        condition = self.current_node.condition_check(self.complete_chatting_messages)
        if condition == "NA":
            if self.clarification_count < self.current_node.max_clarification_attempts:
                clarification_prompt = self._ask_for_question_details(self.complete_chatting_messages)
                msg = assistant_message(clarification_prompt, self.current_node.info)
                messages_to_returned.append(msg)
                self.current_node.chatting_messsages.append(msg)
                self.complete_chatting_messages.append(msg)
                self.clarification_count += 1
                return
            else: 
                condition = "default"

  

        # process parallism_works: use it modify next questoin statement
        logger.info(f"--------   Session {self.session_id}: Processing parallism work --------")
        parallism_work_results = {}
        for pw_callback in self.current_node.parallism_works[condition]:
            pw_callback(
                current_node=self.current_node, 
                messages_to_returned=messages_to_returned,
                chatting_messsages=self.current_node.chatting_messsages,
                complete_chatting_messages=self.complete_chatting_messages,
                parallism_work_results=parallism_work_results,
                condition=condition
            )

        # check if condition valid
        if condition not in  self.current_node.summary_generators:
            raise Exception(f"Condition : {condition} not valid for node summary: {self.current_node.id}.")
        
        # summary
        summary_generator = self.current_node.summary_generators[condition]
        if summary_generator == Signal.SKIP_SUMMARY_SIGNAL:
            logger.info(f"--------   Session {self.session_id}: Skipping Summay --------")
            pass

        elif isinstance(summary_generator, str):
            logger.info(f"--------   Session {self.session_id}: LLM Generating Summay --------")
            msg = assistant_message(summary_generator, self.current_node.info)
            messages_to_returned.append(msg)
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)


        elif isinstance(summary_generator, Callable):
            logger.info(f"--------   Session {self.session_id}: Written Summay --------")
            summary = self.current_node.summary_generators[condition](self.complete_chatting_messages)
            msg = assistant_message(summary, self.current_node.info)
            messages_to_returned.append(msg)
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)



        self.current_node.eof = True
        return condition

        
    def handle_selection_question(self, messages_to_returned) -> str:
        raise NotImplementedError



    def handle_plain_message_question(self, messages_to_returned) -> str:
        raise Exception("Plain message should not be handdled!")
    

    def handle_no_condition_check_question(self, messages_to_returned) -> str:
        """
        After receiving user response, it needs to perform
            1. run parallism_works to condition
            2. run summary generator according to condition
            3. return summary
            4. update eof
        """
        condition = "default"
        # process parallism_works: use it modify next questoin statement
        logger.info(f"--------   Session {self.session_id}: Processing parallism work --------")
        parallism_work_results = {}
        for pw_callback in self.current_node.parallism_works[condition]:
            pw_callback(
                current_node=self.current_node, 
                messages_to_returned=messages_to_returned,
                chatting_messsages=self.current_node.chatting_messsages,
                complete_chatting_messages=self.complete_chatting_messages,
                parallism_work_results=parallism_work_results,

            )

        # check if condition valid
        if condition not in  self.current_node.summary_generators:
            raise Exception(f"Condition : {condition} not valid for node summary: {self.current_node.id}.")
        
        # summary
        summary_generator = self.current_node.summary_generators[condition]
        if summary_generator == Signal.SKIP_SUMMARY_SIGNAL:
            logger.info(f"--------   Session {self.session_id}: Skipping Summay --------")
            pass

        elif isinstance(summary_generator, str):
            logger.info(f"--------   Session {self.session_id}: LLM Generating Summay --------")
            msg = assistant_message(summary_generator, self.current_node.info)
            messages_to_returned.append(msg)
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)


        elif isinstance(summary_generator, Callable):
            logger.info(f"--------   Session {self.session_id}: Written Summay --------")
            summary = self.current_node.summary_generators[condition](self.complete_chatting_messages)
            msg = assistant_message(summary, self.current_node.info)
            messages_to_returned.append(msg)
            self.current_node.chatting_messsages.append(msg)
            self.complete_chatting_messages.append(msg)



        self.current_node.eof = True
        return condition
    

    def handle_end_question(self, messages_to_returned) -> List[Message]:
        raise Exception("The conversation already ended. No next question!")
        

    def _move_to_next_node(self, messages_to_returned, condition="default") -> List[Message]:
        if condition not in self.current_node.next_nodes:
            raise Exception(f"Condition : '{condition}' not valid for node next_nodes: {self.current_node.id}. Next nodes options: {self.current_node.next_nodes}")
        
        logger.info(f"Current node: {self.current_node.id}. Current condition: {condition}.  Next nodes options: {self.current_node.next_nodes}.  Moving to next node: {self.current_node.next_nodes[condition].id}".center(100, "="))
        self.current_node = self.current_node.next_nodes[condition]
        msg = assistant_message(
            node_question_wrapper(
                self.current_node.text,
                self.user_info["user_name"],
            ),
            self.current_node.info,
        )
        messages_to_returned.append(msg)
        self.current_node.chatting_messsages.append(msg)
        self.complete_chatting_messages.append(msg)
        self.clarification_count = 0 
        self._questions_finished += 1

        return "default" # reset condition



  
