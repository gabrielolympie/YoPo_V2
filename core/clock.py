"""
Core concepts and logics:
This module implements a simple clock to track when a neuron was last fired.
The clock maintains a timestamp of the last firing and a count of the total firings.
It provides an update method to refresh the clock when a new firing occurs.
"""

import time

class Clock:
    def __init__(self):
        # Initialize the clock with no last fired time and a fire count of 0
        self.last_fired: float = None
        self.fire_count: int = 0

    def update(self):
        """
        Update the clock by setting the current time as the last fired time and incrementing the fire count.

        Returns:
            None
        """
        # Get the current time using the time module
        self.last_fired = time.time()
        # Increment the fire count by 1
        self.fire_count += 1