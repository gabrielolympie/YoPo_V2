"""
Core concepts and logics:
This module defines the base class for activation functions in a neural network.
The Activation class is an abstract base class that provides a blueprint for routing replies to neuron successors.
The route method must be reimplemented by concrete subclasses to provide the actual routing logic.
"""

from abc import ABC, abstractmethod
from typing import List
from core.message import Message, Reply
from core.neuron import Neuron
from core.st_memory import WorkingMemory

class Activation(ABC):
    """
    Abstract base class for activation functions in a neural network.
    
    Attributes:
        None
    
    Methods:
        route: Routes a reply to the successors of a neuron.
    """
    @abstractmethod
    def route(self, reply: Reply, neuron: Neuron, working_memory:WorkingMemory=None) -> List[Message]:
        """
        Routes a reply to the successors of a neuron.
        
        Args:
            reply (Reply): The reply to be routed.
            neuron (Neuron): The neuron that the reply is being routed from.
        
        Returns:
            List[Message]: A list of messages to be sent to the successors of the neuron.
        """
        # Default implementation, can be overridden by subclasses
        # Create a message for each successor of the neuron
        return [Message(type="empty", sender_id=neuron.sender_id, receiver_id=successor, reply=reply) for successor in neuron.successors]