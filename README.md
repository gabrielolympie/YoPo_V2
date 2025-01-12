# Neural LLM

This is a neural LLM framework designed to facilitate the creation of complex networks. The framework consists of several components, including neurons, steps, activations, and brains.

## Installation

To install the project, run the following command:
```bash
pip install -r requirements.txt
```

## Components

The framework consists of the following components:

* **Neuron**: A neuron represents a node in the neural network. It has attributes such as id, description, predecessors, successors, triggers, step function, activation function, buffer, and clock.
* **Step**: A step represents a single unit of processing in a conversation flow. It has attributes such as str_input and step_args.
* **Activation**: An activation represents a mechanism for routing replies to neuron successors. It has attributes such as type and reply.
* **Brain**: A brain represents a neural network that can execute conversations. It has attributes such as name, neurons, max_working_memory_size, working_memory_overflow_strategy, workers, timeout, iteration_delay, and max_concurrent_fires.

## Examples

Here is an example of how to create a neuron and add it to a brain:
```python
neuron = Neuron(
    id="neuron_1",
    description="the description of the node",
    predecessors={"predecessor_1":"description_1", "predecessor_2":"description_2"},
    successors={"successor_1": "description_1", "successor_2": "description_2"},
    triggers=[trigger_1, trigger_2],
    step=step_function,
    activation=activation_function,
)

brain = Brain(
    name="my_brain",
    neurons=[neuron],
    max_working_memory_size=10000,
    working_memory_overflow_strategy="fifo",
    workers=8,
    timeout=120,
    iteration_delay=0.5,
    max_concurrent_fires=100,
)
```

## Contributing

To contribute to the project, please submit a pull request with your changes. You can also report issues on the issues page.
