# Core concepts and logics:
# This module defines the base class for a step in a conversation flow.
# A step represents a single unit of processing in a conversation, 
# and is responsible for generating a reply based on the conversation context and inputs.

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.message import Message, Reply
from core.st_memory import WorkingMemory

class Step(ABC):
    def __init__(self, str_input: str = None, step_args: Dict[str, Any] = {}):
        """
        Initializes a Step instance.

        Args:
            str_input (str): The input string for the step. To ensure conversation as first class citizen, it handle only strings, you can parse a string in the forward.
            step_args (Dict[str, Any]): Additional arguments for the step.
        """
        self.str_input = str_input
        self.step_args = step_args

    @abstractmethod
    def forward(self, conversation: Dict[str, Any], context: Dict[str, Message], working_memory: WorkingMemory = None) -> Reply:
        """
        Processes the conversation context and inputs to generate a reply.

        Args:
            conversation (Dict[str, Any]): The conversation data.
            context (Dict[str, Message]): The conversation context.
            working_memory (WorkingMemory): The working memory for the conversation.

        Returns:
            Reply: The generated reply.
        """
        pass