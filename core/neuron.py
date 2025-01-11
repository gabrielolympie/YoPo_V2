from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List, Union
import time
import random
import uuid
import yaml

class Synapse(BaseModel):
    sender_neuron_id:str
    receiver_neuron_id:str

class ResetMessage(BaseModel):
    """A message to reset the state of a neuron.

    Attributes:
        id (str): A unique identifier for the reset message.
    """
    id: str
    emitter_id: str
    
class InactiveMessage(BaseModel):
    """An inactive message, that says the neuron does not want to sent its results to its predecessors.

    Attributes:
        id (str): A unique identifier for the reset message.
    """
    id: str
    emitter_id: str   

class Message(BaseModel):
    """A message containing arguments and an optional output.

    Attributes:
        id (str): A unique identifier for the message.
        args (dict): Arguments passed to the neuron (e.g., prompt, query).
        output (Optional[dict]): The output of the neuron, if available.
    """
    id: str
    emitter_id: str
    args: dict = {"prompt": "Hello world"}
    reply: Optional[dict] = {}
    persistant: bool = False


class NeuronArgs(BaseModel):
    args: dict = {"prompt": "Hello world"}
    run_kargs: dict = {}  # Define call arguments
    predecessors: Dict[str, Optional[Union[Message, ResetMessage]]] = {}  # Update type hinting for predecessors
    triggers: List[str] = []  # Change triggers to list of strings
    is_entrypoint: bool = []
    is_terminal: bool = False
    persistant: bool = False

class Neuron(BaseModel):
    """A neuron in a computational graph.

    Attributes:
        id (str): A unique identifier for the neuron.
        args (dict): Arguments passed to the neuron (e.g., prompt, query).
        run_kargs (dict): Runtime arguments for the neuron (e.g., temperature, top_p).
        predecessors (Dict[str, Optional[Union[Message, ResetMessage]]]): Predecessors of the neuron.
        triggers (List[str]): List of trigger strings that determine when the neuron should fire.
        is_terminal (bool): Indicates if the neuron is a terminal node.
    """
    id: str
    args: dict = NeuronArgs().args
    run_kargs: dict = NeuronArgs().run_kargs
    predecessors: Dict[str, Optional[Union[Message, ResetMessage]]] = NeuronArgs().predecessors
    triggers: List[str] = NeuronArgs().triggers
    is_entrypoint: bool = NeuronArgs().is_entrypoint
    is_terminal: bool = NeuronArgs().is_terminal
    persistant: bool = NeuronArgs().persistant

    def forward(self, messages:list, args: dict, run_kargs: dict, run_context: dict) -> Union[Message, ResetMessage, None]:
        """Defines the execution logic for the neuron node.

        Args:
            messages (list): Messages are the main entrypoint, they are define in standard {'role':'user','content':'content'} way.
            args (dict): The arguments passed to the neuron (e.g., prompt, query).
            run_kargs (dict): The runtime arguments for the neuron (e.g., temperature, top_p).
            run_context (dict): The context in which the neuron is running (results of previous nodes).

        Returns:
            reply (dict): the dictionnary of outputs
        """
        time.sleep(random.uniform(0,1))
        return Message(id=str(uuid.uuid4()), emitter_id=self.id, args=args, reply={'content':'ran'}, persistant=False) ## This is just for test, all neuron must be redefined
    
    def fire(self, messages:list, trigger_str: str) -> Union[Message, ResetMessage, None]:
        """Fires the neuron based on the given trigger string.

        Args:
            messages (list): Messages are the main entrypoint, they are define in standard {'role':'user','content':'content'} way.
            trigger_str (str): A string representing the trigger condition.

        Returns:
            Union[Message, ResetMessage, None]: The result of the neuron's forward method.
        """
        triggers=trigger_str.split(',')
        
        run_context={}
        for elt in triggers:
            if elt in self.predecessors:
                run_context[elt]=self.predecessors[elt].copy()
                if not(self.predecessors[elt].persistant):
                    self.predecessors[elt]=None
                    
        return self.forward(messages=messages, args=self.args, run_kargs=self.run_kargs, run_context=run_context)
        
    def ready_to_fire(self) -> Union[str, bool]:
        """Checks if any trigger is ready to fire based on the predecessors.

        Returns:
            Union[str, bool]: A trigger string if ready to fire, otherwise False.
        """
        if len(self.predecessors) == 0:
            return False
        
        triggers = self.triggers.copy()

        if len(triggers) == 0:
            triggers = [','.join(list(self.predecessors.keys()))]
        
        for trigger_str in triggers:
            predecessor_ids = trigger_str.split(',')
            
            if all(self.predecessors[predecessor_id] is not None for predecessor_id in predecessor_ids):
                return trigger_str
            
        return False
    
    def update_predecessor(self, message: Union[Message, ResetMessage]) -> None:
        """Updates the predecessor with the given message or resets it.

        Args:
            message (Union[Message, ResetMessage]): The message to update the predecessor with.
        """
        if isinstance(message, Message):
            self.predecessors[message.emitter_id] = message
        elif isinstance(message, ResetMessage):
            self.predecessors[message.emitter_id] = None
        else:
            raise ValueError("Input must be an instance of Message or ResetMessage.")
    
    @property
    def config(self) -> dict:
        """Returns the neuron configuration as a dictionary, excluding elements with default values.

        Returns:
            dict: The neuron configuration with predecessors set to None and default values excluded.
        """
        default_args = NeuronArgs()
        config_dict = self.dict()
        config_dict['predecessors'] = {key: None for key in config_dict['predecessors']}
        
        for key, default_value in default_args.dict().items():
            if config_dict[key] == default_value:
                del config_dict[key]
        
        return config_dict

    def save_config(self, file_path: str) -> None:
        """Saves the neuron configuration to a YAML file.

        Args:
            file_path (str): The path to the YAML file.
        """
        with open(file_path, 'w') as file:
            yaml.dump(self.config, file)

    @classmethod
    def load_config(cls, file_path: str) -> 'Neuron':
        """Loads the neuron configuration from a YAML file.

        Args:
            file_path (str): The path to the YAML file.

        Returns:
            Neuron: An instance of the Neuron class with the loaded configuration.
        """
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict)

    def add_predecessor(self, predecessor_id: str) -> None:
        """Adds a predecessor with the given ID and initializes it to None.

        Args:
            predecessor_id (str): The ID of the predecessor to add.
        """
        self.predecessors[predecessor_id] = None

    def remove_predecessor(self, predecessor_id: str) -> None:
        """Removes the predecessor with the given ID and updates triggers.

        Args:
            predecessor_id (str): The ID of the predecessor to remove.
        """
        if predecessor_id in self.predecessors:
            del self.predecessors[predecessor_id]
            self.triggers = [trigger for trigger in self.triggers if predecessor_id not in trigger.split(',')]

    def reset_predecessor(self, predecessor_id: str) -> None:
        """Clears the predecessor with the given ID.

        Args:
            predecessor_id (str): The ID of the predecessor to reset.
        """
        self.predecessors[predecessor_id] = None

    def add_trigger(self, trigger_str: str) -> None:
        """Adds a trigger string after validating its components.

        Args:
            trigger_str (str): The trigger string to add.

        Raises:
            ValueError: If any trigger ID is not in predecessors.
        """
        trigger_ids = trigger_str.split(',')
        if not all(trigger_id in self.predecessors for trigger_id in trigger_ids):
            raise ValueError(f"All trigger IDs must be in predecessors. Invalid IDs: {trigger_ids}")
        self.triggers.append(trigger_str)

    def remove_trigger(self, trigger_str: str) -> None:
        """Removes a trigger string from the triggers list.

        Args:
            trigger_str (str): The trigger string to remove.

        Raises:
            ValueError: If the trigger string is not found in triggers.
        """
        if trigger_str in self.triggers:
            self.triggers.remove(trigger_str)
        else:
            raise ValueError(f"Trigger '{trigger_str}' not found in triggers.")