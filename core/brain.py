import networkx as nx
from core.neuron import Neuron, Synapse  # Adjust the import based on your file structure

class Brain:
    def __init__(self, name):
        self.gname = name
        self.neurons = {}
        self.synapses = []
        

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
        self.graph=nx.DiGraph()
        
        for neuron_id, neuron in self.neurons.items():
            self.graph.add_node(neuron_id, **neuron.__dict__)
            
        for sender_neuron_id, receiver_neuron_id in self.synapses:
            self.graph.add_edge(sender_neuron_id, receiver_neuron_id)  # Add synapses as directed edges to the graph
