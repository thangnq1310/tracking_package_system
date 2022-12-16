from dataclasses import dataclass
from queue import PriorityQueue


@dataclass
class Process:
    process_id: int
    priority: int
    burst_time: float
    remaining_time: float
    arrival_time: float


class MultilevelQueue:
    def __init__(self):
        self.time_quantum = 4

    def round_robin(self, queue, size):
        i = 0
        time = 0
        flag = 0
        remain = size
        while remain != 0:
            p = queue[i]
            if self.time_quantum >= p.remaining_time > 0:
                time += p.remaining_time
                p.remaining_time = 0
                flag = 1
            elif p.remaining_time > self.time_quantum:
                p.remaining_time -= self.time_quantum
                time += self.time_quantum

            if p.remaining_time == 0 and flag == 1:
                remain -= 1
                flag = 0

            if i == remain - 1:
                i = 0
            elif queue[i + 1].arrival_time < time:
                i += 1
            else:
                i = 0

            queue[i] = p

    def priority(self, process, size):
        for i in range(size):
            for j in range(size):
                if process[j].priority > process[i].priority:
                    temp = process[i]
                    process[i] = process[j]
                    process[j] = temp
