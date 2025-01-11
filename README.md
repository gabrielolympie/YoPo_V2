# YoPo_V2
You Only Prompt Once V2 - Declarative Language for Prompting Graph Workflows

## Overview
YoPo_V2 is a framework designed to facilitate the creation and management of computational graphs for prompt-based workflows. It allows users to define and execute complex workflows declaratively, where each node in the graph (referred to as a "neuron") can process inputs, generate outputs, and interact with other neurons based on specified triggers.

## Key Components

### Neuron
A `Neuron` is a fundamental unit in the computational graph. Each neuron has the following attributes:
- **id**: A unique identifier for the neuron.
- **args**: Arguments passed to the neuron, such as prompts or queries.
- **run_kargs**: Runtime arguments for the neuron, such as temperature or top_p.
- **predecessors**: A dictionary of predecessor neurons or reset messages.
- **triggers**: A list of trigger strings that determine when the neuron should execute.
- **is_terminal**: A boolean indicating if the neuron is a terminal node.

### Message and ResetMessage
- **Message**: Represents a message containing arguments and an optional output.
- **ResetMessage**: A special type of message used to reset the state of a neuron.

### Methods
- **forward**: Defines the execution logic for the neuron. It takes arguments, runtime arguments, and a runtime context, and returns a `Message`, `ResetMessage`, or `None`.
- **config**: Returns the neuron configuration as a dictionary, with predecessors set to `None`.
- **load_config**: Loads the neuron configuration from a YAML file.

## Usage
To use YoPo_V2, define your computational graph by creating instances of `Neuron` and configuring their attributes and triggers. You can then execute the graph by calling the `forward` method on the neurons, passing the necessary arguments and context.

For more detailed usage and examples, refer to the documentation or the example files provided with the project.