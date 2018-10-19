""" Shingle is used with RCF, as fifo queue of last n metrics. """
import queue

class Shingle:

    def __init__(self, size):
        self.shingle = queue.Queue(maxsize=size)
        # TODO delete this as it is for tests only
        self.push(238)
        self.push(226)
        self.push(228)
        self.push(219)
        self.push(236)
        self.push(236)
        self.push(207)
        self.push(255)
        self.push(192)
        self.push(222)
        self.push(250)
        self.push(220)

    def push(self, value):
        if self.shingle.full():
            self.shingle.get_nowait()
        self.shingle.put(value)

    def is_ready(self):
        return self.shingle.full()

    def to_csv(self):
        result = ','.join(['%d' % num for num in list(self.shingle.queue)]) + '\n'
        return result

