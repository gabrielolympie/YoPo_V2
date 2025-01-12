"""
Core concepts and logics:
This module defines the core data structures for messages in the system.
It includes MessageType Enum, Reply and Message models.
The MessageType Enum defines the types of messages that can be sent.
The Reply model represents the response to a message, containing inputs, outputs and metadata.
The Message model represents a message, containing its type, sender and receiver IDs, reply, priority, creation time and metadata.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any
import time

class MessageType(str, Enum):
    """Enum representing the types of messages."""
    EMPTY = "empty"
    PERSISTENT = "persistent"
    PAYLOAD = "payload"

class Reply(BaseModel):
    """Model representing the response to a message."""
    str_input: str
    str_output: str
    context: list = None
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata of the reply

class Message(BaseModel):
    """Model representing a message."""
    type: MessageType  # Type of the message
    sender_id: str = None  # ID of the sender
    receiver_id: str = None  # ID of the receiver
    reply: Reply = None  # Reply to the message
    priority: int = Field(default=0, ge=0, le=10)  # Priority of the message
    created_at: float = Field(default_factory=lambda: time.time())  # Time the message was created
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata of the message

    @staticmethod
    def validate_priority(v):
        """Validate the priority value."""
        # Check if the priority is within the valid range
        if not (0 <= v <= 10):
            raise ValueError("Priority must be between 0 and 10")
        return v