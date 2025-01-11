import networkx as nx
from core.neuron import Neuron, Synapse  # Adjust the import based on your file structure
import yaml
import os

class Brain:
    def __init__(self, name):
        self.gname = name
        self.neurons = {}
        self.synapses = []
        self.build()

    def add_neuron(self, neuron: Neuron):
        if not isinstance(neuron, Neuron):
            raise ValueError("Node must be an instance of Neuron.")
        self.neurons[neuron.id] = neuron
        self.build()

    def add_synapse(self, synapse: Synapse):
        if not isinstance(synapse, Synapse):
            raise ValueError("Synapse must be an instance of Synapse.")
        self.synapses.append((synapse.sender_neuron_id, synapse.receiver_neuron_id))
        self.build()

    def remove_neuron(self, id):
        self.synapses = [synapse for synapse in self.synapses if id not in synapse]
        self.neurons = {neuron_id: neuron for neuron_id, neuron in self.neurons.items() if neuron_id != id}
        self.build()

    def remove_synapse(self, sender_neuron_id, receiver_neuron_id):
        self.synapses = [synapse for synapse in self.synapses if synapse != (sender_neuron_id, receiver_neuron_id)]
        self.build()

    def build(self):
        self.graph = nx.DiGraph()

        for neuron_id, neuron in self.neurons.items():
            self.graph.add_node(neuron_id, **neuron.config)  # Use neuron.config to avoid saving predecessors

        for sender_neuron_id, receiver_neuron_id in self.synapses:
            self.graph.add_edge(sender_neuron_id, receiver_neuron_id)  # Add synapses as directed edges to the graph

    @property
    def config(self) -> dict:
        """Saves the brain configuration as a dictionary.

        Returns:
            dict: The brain configuration including neurons and synapses.
        """
        neuron_configs = {neuron_id: neuron.config for neuron_id, neuron in self.neurons.items()}
        formatted_synapses = [f"{sender} -> {receiver}" for sender, receiver in self.synapses]
        return {
            "name": self.gname,
            "neurons": neuron_configs,
            "synapses": formatted_synapses
        }

    @classmethod
    def from_config(cls, config: dict) -> 'Brain':
        """Loads the brain configuration from a dictionary.

        Args:
            config (dict): The brain configuration including neurons and synapses.

        Returns:
            Brain: An instance of the Brain class with the loaded configuration.
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

    def save_config(self, file_path: str):
        """Saves the brain configuration to a YAML file.

        Args:
            file_path (str): The path to the YAML file.
        """
        with open(file_path, 'w') as file:
            yaml.dump(self.config, file)

    @classmethod
    def load_config(cls, file_path: str) -> 'Brain':
        """Loads the brain configuration from a YAML file.

        Args:
            file_path (str): The path to the YAML file.

        Returns:
            Brain: An instance of the Brain class with the loaded configuration.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return cls.from_config(config)