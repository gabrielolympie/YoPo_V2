"""
core/buffer.py

This module provides a Buffer class to store messages from predecessors.
It handles receiving messages, cleaning up stale messages, and providing context for predecessors.
"""

from typing import Dict, List
from core.message import Message, MessageType
import time
import logging

logger = logging.getLogger(__name__)

class Buffer:
    def __init__(self, predecessors_ids: List[str], max_age: float = None):
        """
        Initializes the Buffer instance.

        Args:
            predecessors_ids (List[str]): A list of predecessor IDs.
            max_age (float): The maximum age of a message before it is considered stale. Defaults to None.
        """
        # Initialize the buffer with empty messages for each predecessor
        self.messages = {predecessor: Message(type=MessageType.EMPTY) for predecessor in predecessors_ids}
        self.message_timestamps = {predecessor: time.time() for predecessor in predecessors_ids}
        self.max_age = max_age

    def receive(self, message: Message):
        """
        Receive a message from a predecessor.

        Args:
            message (Message): The message to receive.
        """
        # Get the sender ID from the message
        sender_id = message.sender_id
        # Check if the sender ID is in the buffer's messages
        if sender_id in self.messages:
            # Update the message and timestamp for the sender ID
            self.messages[sender_id] = message
            self.message_timestamps[sender_id] = time.time()

    def cleanup_stale_messages(self):
        """
        Clean up stale messages from the buffer.
        """
        # Check if max_age is set
        if self.max_age is None:
            # If not, do nothing
            return

        # Get the current time
        current_time = time.time()
        # Iterate over the predecessors in the buffer
        for predecessor in self.messages:
            # Check if the message is stale (i.e., its age exceeds max_age)
            if current_time - self.message_timestamps[predecessor] > self.max_age:
                # If stale, reset the message to EMPTY
                self.messages[predecessor] = Message(type=MessageType.EMPTY)

    def clear(self):
        """
        Clear the buffer.
        """
        # Iterate over the predecessors and their messages in the buffer
        for predecessor, buffered_message in self.messages.items():
            # Check if the message is not PERSISTENT
            if buffered_message.type != MessageType.PERSISTENT:
                # If not, reset the message to EMPTY
                self.messages[predecessor] = Message(type=MessageType.EMPTY)

    def get_context(self, predecessors_ids: List[str]):
        """
        Get the context for a list of predecessors.

        Args:
            predecessors_ids (List[str]): A list of predecessor IDs.

        Returns:
            Dict[str, Message]: A dictionary of messages for the given predecessors.
        """
        # Return a dictionary of messages for the given predecessors
        return {k: self.messages[k] for k in predecessors_ids}

    def __call__(self, predecessor_id: str):
        """
        Get the message for a given predecessor.

        Args:
            predecessor_id (str): The ID of the predecessor.

        Returns:
            Message: The message for the given predecessor.
        """
        # Return the message for the given predecessor ID
        return self.messages[predecessor_id]