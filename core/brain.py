import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import yaml
import time
import os

from core.neuron import Neuron, Synapse, Message, InactiveMessage, ResetMessage

class Brain:
    """
    A class representing a brain with neurons and synapses.

    Attributes:
        name (str): The name of the brain.
        neurons (dict): A dictionary of neurons in the brain.
        synapses (list): A list of synapses in the brain.
        entry_nodes (list): A list of entry nodes in the brain.
        terminal_nodes (list): A list of terminal nodes in the brain.
        workers (int): The number of workers for the brain.
        timeout (int): The timeout for the brain.
        clock_frequency (float): The clock frequency for the brain.
    """

    def __init__(self, name, workers=8, timeout=120, clock_frequency=0.1):
        """
        Initializes a Brain object.

        Args:
            name (str): The name of the brain.
            workers (int, optional): The number of workers for the brain. Defaults to 8.
            timeout (int, optional): The timeout for the brain. Defaults to 120.
            clock_frequency (float, optional): The clock frequency for the brain. Defaults to 0.1.
        """
        self.name = name
        self.neurons = {}
        self.synapses = []
        self.entry_nodes = []
        self.terminal_nodes = []
        
        self.workers = workers
        self.timeout = timeout
        self.clock_frequency = clock_frequency
        
        self.build()
        
    def run(self, messages):
        """
        Runs the brain with the given messages.

        Args:
            messages: The messages to run the brain with.

        Yields:
            Message: The messages produced by the brain.
        """
        assert len(self.entry_nodes) + len(self.terminal_nodes) > 0, "The graph must have at least one entry point or one terminal node"
        
        executor = ThreadPoolExecutor(max_workers=32)
        start_time = time.time()
        futures = []
        
        for entry_node in self.entry_nodes:
            futures.append(executor.submit(self.neurons[entry_node].fire, messages, ""))
        
        cond = True
        while cond:
            for future in futures[:]:
                if future.done():
                    result = future.result()
                    if not isinstance(result, InactiveMessage):
                        if isinstance(result, Message):
                            yield result
                        if self.neurons[result.emitter_id].is_terminal:
                            cond = False
                        
                        for successor in self.successors(result.emitter_id):
                            self.neurons[successor].update_predecessor(result)
                    futures.remove(future)
                    
            time.sleep(self.clock_frequency)
            for neuron in self.neurons:
                should_fire = self.neurons[neuron].ready_to_fire()    
                if should_fire is not False:
                    futures.append(executor.submit(self.neurons[neuron].fire, messages, should_fire))
                    
            if time.time() - start_time > self.timeout:
                cond = False
                yield "Stopped due to the duration exceeding the set timeout"

    def successors(self, node_id):
        """
        Gets the successors of a node.

        Args:
            node_id: The ID of the node.

        Returns:
            list: The successors of the node.
        """
        return [receiver for sender, receiver in self.synapses if sender == node_id]    
    
    def build(self):
        """
        Builds the brain graph.
        """
        self.graph = nx.DiGraph()

        for neuron_id, neuron in self.neurons.items():
            self.graph.add_node(neuron_id, **neuron.config)  # Use neuron.config to avoid saving predecessors

        for sender_neuron_id, receiver_neuron_id in self.synapses:
            self.graph.add_edge(sender_neuron_id, receiver_neuron_id)  # Add synapses as directed edges to the graph

        self.entry_nodes = [neuron_id for neuron_id, neuron in self.neurons.items() if neuron.is_entrypoint]
        self.terminal_nodes = [neuron_id for neuron_id, neuron in self.neurons.items() if neuron.is_terminal]
        
    def add_neuron(self, neuron):
        """
        Adds a neuron to the brain.

        Args:
            neuron (Neuron): The neuron to add.

        Raises:
            ValueError: If the neuron is not an instance of Neuron.
        """
        if not isinstance(neuron, Neuron):
            raise ValueError("Node must be an instance of Neuron.")
        self.neurons[neuron.id] = neuron
        self.build()

    def add_synapse(self, synapse):
        """
        Adds a synapse to the brain.

        Args:
            synapse (Synapse): The synapse to add.

        Raises:
            ValueError: If the synapse is not an instance of Synapse.
        """
        if not isinstance(synapse, Synapse):
            raise ValueError("Synapse must be an instance of Synapse.")
        self.synapses.append((synapse.sender_neuron_id, synapse.receiver_neuron_id))
        self.build()

    def remove_neuron(self, id):
        """
        Removes a neuron from the brain.

        Args:
            id: The ID of the neuron to remove.
        """
        self.synapses = [synapse for synapse in self.synapses if id not in synapse]
        self.neurons = {neuron_id: neuron for neuron_id, neuron in self.neurons.items() if neuron_id != id}
        self.build()

    def remove_synapse(self, sender_neuron_id, receiver_neuron_id):
        """
        Removes a synapse from the brain.

        Args:
            sender_neuron_id: The ID of the sender neuron.
            receiver_neuron_id: The ID of the receiver neuron.
        """
        self.synapses = [synapse for synapse in self.synapses if synapse != (sender_neuron_id, receiver_neuron_id)]
        self.build()

    @property
    def config(self):
        """
        Gets the brain configuration.

        Returns:
            dict: The brain configuration.
        """
        neuron_configs = {neuron_id: neuron.config for neuron_id, neuron in self.neurons.items()}
        formatted_synapses = [f"{sender} -> {receiver}" for sender, receiver in self.synapses]
        return {
            "name": self.name,
            "workers": self.workers,
            "timeout": self.timeout,
            "neurons": neuron_configs,
            "synapses": formatted_synapses,
            "entry_nodes": self.entry_nodes,
            "terminal_nodes": self.terminal_nodes
        }

    @classmethod
    def from_config(cls, config):
        """
        Creates a Brain object from a configuration.

        Args:
            config (dict): The brain configuration.

        Returns:
            Brain: The created Brain object.
        """
        brain = cls(config["name"])
        for neuron_id, neuron_config in config["neurons"].items():
            neuron = Neuron(**neuron_config)
            brain.add_neuron(neuron)
        for synapse_str in config["synapses"]:
            sender_neuron_id, receiver_neuron_id = synapse_str.split(" -> ")
            synapse = Synapse(sender_neuron_id=sender_neuron_id, receiver_neuron_id=receiver_neuron_id)
            brain.add_synapse(synapse)
        return brain

    def save_config(self, file_path):
        """
        Saves the brain configuration to a file.

        Args:
            file_path (str): The path to the file.
        """
        with open(file_path, 'w') as file:
            yaml.dump(self.config, file)

    @classmethod
    def load_config(cls, file_path):
        """
        Loads a Brain object from a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            Brain: The loaded Brain object.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return cls.from_config(config)