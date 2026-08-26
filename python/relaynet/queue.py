from collections import deque


class RelayQueue:

    def __init__(self, capacity=20):
        self.capacity = capacity
        self.packets = deque()

    def enqueue(self, packet, time_step):
        if self.is_full():
            return False

        self.packets.append(
            (packet, time_step)
        )

        return True

    def dequeue(self):
        if not self.packets:
            return None

        return self.packets.popleft()

    def is_full(self):
        return len(self.packets) >= self.capacity

    def size(self):
        return len(self.packets)

    def waiting_time(self, current_time):
        if not self.packets:
            return 0

        _, arrival_time = self.packets[0]

        return current_time - arrival_time