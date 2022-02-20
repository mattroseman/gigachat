import threading


class CircularBuffer:
    def __init__(self, capacity):
        self.size = 0
        self.capacity = capacity
        self._head = 0
        self._queue = [None] * capacity
        self._lock = threading.Lock()

    def enqueue(self, item):
        with self._lock:
            self._queue[self._head] = item

            self._head += 1
            self._head %= self.capacity

            self.size = min(self.size + 1, self.capacity)

    def get(self):
        # result = []

        # i = (self._head - 1) % self.capacity
        # while i != self._head:
        #     result.append(self._queue[i].message)
        #     i -= 1
        #     i %= self.capacity

        # return result

        return [item for item in (self._queue[self._head - 1:] + self._queue[:self._head - 1]) if item is not None]

    def __str__(self):
        return '\n'.join([str(item) for item in self.get()])
