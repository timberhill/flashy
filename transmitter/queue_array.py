from queue import Queue


class QueueArray:
    def __init__(self, length, size):
        self.length = length
        self.queues = [Queue(size) for i in range(self.length)]
    
    def full(self, index):
        return self.queues[index].full()
    
    def empty(self, index):
        return self.queues[index].empty()
    
    def qsize(self, index=None):
        if index is None:
            return [self.queues[i].qsize() for i in range(self.length)]
        return self.queues[index].qsize()
    
    def put(self, index, item):
        return self.queues[index].put(item)
    
    def get(self, index):
        return self.queues[index].get()