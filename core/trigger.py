"""
Core concepts and logics:
This module defines the base class for triggers in the neural network.
A trigger is an abstract concept that determines when a neuron should be activated.
The condition method is used to evaluate the trigger condition for a given neuron.
"""
from abc import ABC, abstractmethod
from core.neuron import Neuron

class Trigger(ABC):
    """
    Abstract base class for triggers in the neural network.
    
    Attributes:
        None
    
    Methods:
        condition: Evaluates the trigger condition for a given neuron.
    """
    @abstractmethod
    def condition(self, neuron: Neuron) -> list|None:
        """Evaluates the trigger condition for a given neuron.

        Args:
            neuron (Neuron): The neuron to evaluate the condition for.
        
        Returns:
            list|None: A subset of the neuron predecessors if triggered, else None.
        """
        pass