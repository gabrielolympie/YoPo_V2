import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from core.neuron import Neuron
from core.st_memory import WorkingMemory
import time
import logging

logger = logging.getLogger(__name__)

class Brain:
    def __init__(
        self, 
        name: str, 
        neurons: List[Neuron], 
        max_working_memory_size: int = int(1e5),
        working_memory_overflow_strategy: str = 'fifo', 
        workers: int = 8,
        timeout: int = 120,
        iteration_delay: float = 0.5,
        max_concurrent_fires: int = 100,
    ):
        """
        Initializes the Brain instance.

        Args:
            name (str): The name of the brain.
            neurons (List[Neuron]): The list of neurons in the brain.
            max_working_memory_size (int, optional): The maximum size of the working memory. Defaults to 1e5.
            working_memory_overflow_strategy (str, optional): The strategy to use when the working memory overflows. Defaults to 'fifo'.
            workers (int, optional): The number of worker threads. Defaults to 8.
            timeout (int, optional): The timeout for the brain execution. Defaults to 120.
            iteration_delay (float, optional): The delay between iterations. Defaults to 0.5.
            max_concurrent_fires (int, optional): The maximum number of concurrent fires. Defaults to 100.
        """
        self.name = name
        self.neurons = {neuron.id: neuron for neuron in neurons}
        self.max_working_memory_size = max_working_memory_size
        self.working_memory_overflow_strategy = working_memory_overflow_strategy
        self.workers = workers
        self.timeout = timeout
        self.iteration_delay = iteration_delay
        self.max_concurrent_fires = max_concurrent_fires
        self.working_memory = WorkingMemory(max_working_memory_size=self.max_working_memory_size, working_memory_overflow_strategy=self.working_memory_overflow_strategy)
        self.active_fires = 0

    def run(self, conversation):
        """
        Runs the brain execution synchronously.

        Args:
            conversation: The conversation to execute. Conversation a list of dict [{'role':'user','content':'Hello World'}]

        Yields:
            List: The list of messages each time a process is finished. They are yielded as Message class
        """
        # Create a thread pool executor with the specified number of workers
        executor = ThreadPoolExecutor(max_workers=self.workers)
        start_time = time.time()
        futures = []

        try:
            # Submit the entry nodes for execution
            for entry_node in self.entry_nodes:
                # Wait if the maximum number of concurrent fires is reached
                while self.active_fires >= self.max_concurrent_fires:
                    time.sleep(0.1)
                
                self.active_fires += 1
                # Submit the fire_with_retry task to the executor
                futures.append(executor.submit(self.neurons[entry_node].fire_with_retry, conversation, []))

            # Continuously check for completed futures and new neurons to fire
            while True:
                # Check for timeout
                if time.time() - start_time > self.timeout:
                    logger.warning(f"Brain {self.name} execution timed out")
                    break

                # Process completed futures
                for future in futures[:]:
                    if future.done():
                        try:
                            result = future.result()
                            
                            if result:
                                neuron, reply, messages = result

                                ## Yield the reply in textual format
                                yield reply
                                
                                ## Update the ran neuron
                                self.neurons[neuron.id] = neuron
                                    
                                for message in messages:
                                    # Receive the message and append it to the working memory
                                    self.neurons[message.receiver_id].receive(message)
                                    self.working_memory.append(message)
                                        
                        except Exception as e:
                            logger.error(f"Error processing future: {str(e)}")
                        finally:
                            # Decrement the active fires count and remove the future
                            self.active_fires -= 1
                            futures.remove(future)

                # Check for new neurons to fire
                for neuron_id, neuron in self.neurons.items():
                    should_fire = neuron.should_fire()
                    if should_fire is not None and self.active_fires < self.max_concurrent_fires:
                        # Increment the active fires count and submit the fire_with_retry task
                        self.active_fires += 1
                        futures.append(executor.submit(neuron.fire_with_retry, conversation, should_fire, self.working_memory))

                # Wait for the iteration delay
                time.sleep(self.iteration_delay)

                # Break if no active futures and no neurons ready to fire
                if not futures and not any(n.should_fire() for n in self.neurons.values()):
                    break

        except Exception as e:
            logger.error(f"Error in brain execution: {str(e)}")
            raise
        finally:
            # Shutdown the executor
            executor.shutdown(wait=True)

    @property
    def entry_nodes(self):
        """
        Gets the entry nodes of the brain.

        Returns:
            List[str]: The list of entry node IDs.
        """
        # Filter the neurons to get the entry nodes
        return [neuron_id for neuron_id, neuron in self.neurons.items() if neuron.is_entrypoint]