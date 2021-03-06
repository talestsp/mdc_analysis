from __future__ import print_function
import psutil
import time

class ResourceUsage:

    def __init__(self):
        pass

    def start(self):
        self.start_time = time.time()
        self.start_memo = psutil.virtual_memory().used

    def check(self):
        print(round(self.check_time(), 2), "secs")
        print(round(self.check_memo() / (1024 * 1024), 2), "MB")

    def check_time(self):
        return time.time() - self.start_time

    def check_memo(self):
        return psutil.virtual_memory().used - self.start_memo
