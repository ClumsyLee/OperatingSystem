from queue import Queue
from threading import Thread, Lock
from time import sleep

class SortJob(object):
    """docstring for SortJob"""
    def __init__(self, l, begin, end, lock):
        super().__init__()

        self.l = l
        self.begin = begin
        self.end = end
        self.lock = lock

    def run(self, pool):
        if self.l is None:  # A padding.
            return True

        with self.lock:
            part = self.l[self.begin:self.end]

        if len(part) < 1000:
            part.sort()
            with self.lock:
                self.l[self.begin:self.end] = part
        else:
            mid = len(part) // 2
            pivot = sorted([part[0], part[mid], part[-1]])[1]

            left = []
            equal = []
            right = []
            for x in part:
                if x < pivot:
                    left.append(x)
                elif x == pivot:
                    equal.append(x)
                else:
                    right.append(x)

            part = left + equal + right

            with self.lock:
                self.l[self.begin:self.end] = part

            separate1 = self.begin + len(left)
            separate2 = self.end - len(right)
            pool.add_job(SortJob(self.l, self.begin, separate1, self.lock))
            pool.add_job(SortJob(self.l, separate2, self.end, self.lock))

        return False

class ThreadPool(object):
    def __init__(self, size):
        super().__init__()

        self.jobs = Queue()
        self.monitors = [Thread(target=self.monitor)
                         for i in range(size)]
        for monitor in self.monitors:
            monitor.start()

        self.jobs_left = 0
        self.jobs_left_lock = Lock()

    def monitor(self):
        while True:
            job = self.jobs.get()
            if job.run(self):  # run return true, so we should quit.
                return

            with self.jobs_left_lock:
                self.jobs_left -= 1
                if self.jobs_left == 0:
                    # No more jobs.
                    # Other monitors are waiting.
                    # Add padding jobs.
                    self.__add_padding_jobs()

    def add_job(self, job):
        with self.jobs_left_lock:
            self.jobs_left += 1
        self.jobs.put(job)

    def join(self):
        for monitor in self.monitors:
            monitor.join()

    def __add_padding_jobs(self):
        for i in range(len(self.monitors)):
            self.jobs.put(SortJob(None, None, None, None))  # Do NOT use add_job


if __name__ == '__main__':
    numbers = []

    with open('random.txt') as f:
        for line in f:
            numbers.append(float(line))

    lock = Lock()
    pool = ThreadPool(20)
    pool.add_job(SortJob(numbers, 0, len(numbers), lock))
    pool.join()

    # Test
    last = -1
    for x in numbers:
        if last > x:
            print('Not sorted.')
            break
        last = x
    else:
        print('sorted.')

    with open('sorted.txt', 'w') as f:
        for number in numbers:
            print('{:6f}'.format(number), file=f)


