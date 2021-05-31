from queue import Queue


class QueueArray:
    """Contains an array of queue objects - one per LED.

    Args:
        length (int): length of the array - number of queues corresponding to the number of the LEDs
        size (int): maximum length of each individual queue
    
    Attributes:
        length (int): length of the array
        queues (list): list of queue objects
    """
    def __init__(self, length, size):
        self.length = length
        self.queues = [Queue(size) for i in range(self.length)]
    
    def full(self, index):
        """Is the queue full.

        Args:
            index (int): index of the queue in array

        Returns:
            bool: True if the queue is full, False otherwise
        """
        return self.queues[index].full()
    
    def empty(self, index):
        """Is the queue empty.

        Args:
            index (int): index of the queue in array

        Returns:
            bool: True if the queue is empty, False otherwise
        """
        return self.queues[index].empty()
    
    def qsize(self, index=None):
        """Size of the queue.

        Args:
            index (int): index of the queue in array (optional)

        Returns:
            int/list: size of the queue at the index or a list of sizes of all queues
        """
        if index is None:
            return [self.queues[i].qsize() for i in range(self.length)]

        return self.queues[index].qsize()
    
    def put(self, index, item):
        """Put an item into a queue.

        Args:
            index (int): index of the queue in array
            item: object to add to the queue
        """
        self.queues[index].put(item)
    
    def get(self, index):
        """Retrieve an item from a queue.

        Args:
            index (int): index of the queue in array

        Returns:
            item: object retrieved from the queue
        """
        return self.queues[index].get()
