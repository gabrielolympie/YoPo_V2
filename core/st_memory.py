from core.message import Message
from typing import Dict, Any, List

class WorkingMemory:
    def __init__(self, max_working_memory_size: int = int(1e5), working_memory_overflow_strategy: str = 'fifo'):
        """
        Initializes a WorkingMemory instance.

        Args:
            max_working_memory_size (int): The maximum size of the working memory. Defaults to 1e5.
            working_memory_overflow_strategy (str): The strategy to use when the working memory overflows. Defaults to 'fifo'.
        """
        self.working_memory_size = 0
        self.max_working_memory_size = max_working_memory_size
        self.working_memory_overflow_strategy = working_memory_overflow_strategy
        self.messages = []

    def overflow(self):
        """
        Handles working memory overflow by implementing the chosen strategy.
        """
        if self.working_memory_size > self.max_working_memory_size:
            if self.working_memory_overflow_strategy == "fifo":
                # Remove oldest messages
                self.messages = self.messages[-self.max_working_memory_size:]
            elif self.working_memory_overflow_strategy == "lifo":
                # Remove newest messages
                self.messages = self.messages[:self.max_working_memory_size]
            self.working_memory_size = self.max_working_memory_size

    def append(self, message: Message):
        """
        Appends a message to the working memory and sorts the working memory by priority and creation time.

        Args:
            message (Message): The message to append.
        """
        self.messages.append(message)
        # Sort by priority (desc) and then by creation time (asc)
        self.messages.sort(key=lambda x: (-x.priority, x.created_at))
        self.working_memory_size = len(self.messages)
        self.overflow()

    def get_messages_by_filter(self, filter_criteria: Dict[str, Any]) -> List[Message]:
        """
        Retrieves messages from the working memory that match the given filter criteria.

        Args:
            filter_criteria (Dict[str, Any]): A dictionary of attribute names and values to filter messages by.

        Returns:
            List[Message]: A list of messages that match the filter criteria.
        """
        filtered_messages = []
        for message in self.messages:
            match = True
            for attr, value in filter_criteria.items():
                if getattr(message, attr, None) != value:
                    match = False
                    break
            if match:
                filtered_messages.append(message)
        return filtered_messages