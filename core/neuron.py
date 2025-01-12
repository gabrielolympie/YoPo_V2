"""
Core concepts and logics:
This module implements a Neuron class, which represents a node in a neural network.
The Neuron class has methods to fire the neuron, handle retries, and check if the neuron should fire.
The neuron's behavior is determined by its step function, activation function, and triggers.
The neuron also has a buffer to store messages and a clock to track time.
"""

from typing import Dict, List, Any

from core.message import Message, MessageType
from core.buffer import Buffer
from core.clock import Clock

import time
import logging

logger = logging.getLogger(__name__)

class Neuron:
    def __init__(
        self, 
        id: str,
        description:str= None,
        predecessors: Dict[str, Any] = {},
        successors: Dict[str, Any] = {},
        triggers: List = [],
        step=None,
        activation=None,
        is_entrypoint: bool = False,
        is_terminal: bool = False,
        max_retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        A neuron in the network.

        Args:
            id (str): The ID of the neuron.
            predecessors (dict[str]): A dictionnary of predecessor IDs and their description as value.
            successors (dict[str]): A dictionnary of successor IDs and their description as value.
            triggers (List): A list of triggers for the neuron.
            step: The step function for the neuron.
            activation: The activation function for the neuron.
            is_entrypoint (bool): Whether the neuron is an entry point.
            is_terminal (bool): Whether the neuron is a terminal.
            max_retry_attempts (int): The maximum number of retry attempts.
            retry_delay (float): The delay between retry attempts.
        """
        self.id = id
        self.predecessors = predecessors
        self.successors = successors
        self.triggers = triggers
        self.step = step
        self.activation = activation
        self.is_entrypoint = is_entrypoint
        self.is_terminal = is_terminal
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay = retry_delay
        # Initialize the buffer with the predecessor IDs and a max age of 5 minutes
        self.buffer = Buffer(predecessors_ids=self.predecessors.keys(), max_age=300)  
        self.clock = Clock()
        
    def receive(self, message:Message):
        self.buffer.receive(message)

    def fire(self, messages, context, working_memory=None):
        """
        Fire the neuron.

        Args:
            messages: The messages to fire.
            context: The context for the fire.

        Returns:
            tuple: A tuple containing the result and messages.
        """
        # Clean up stale messages from the buffer
        self.buffer.cleanup_stale_messages()
        # Get the reply from the step function
        reply = self.step.forward(messages, self.buffer.get_context(context), working_memory=None)
        # Map the reply to the successors using the activation function
        messages = self.activation.route(reply, self, working_memory=None)
        
        # Clear the buffer from all non persistent message
        self.buffer.clear() 
        # Update the clock
        self.clock.update()
        
        return self, reply, messages

    def should_fire(self):
        """
        Check if the neuron should fire.

        Returns:
            context: The context for the fire, or None if the neuron should not fire.
        """
        # If the clock has not been updated, update it
        if self.clock.last_fired is None:
            self.clock.update()
            
        # Check each trigger to see if the neuron should fire
        for trigger in self.triggers:
            context = trigger.condition(self)
            if context is not None:
                return context
        return None