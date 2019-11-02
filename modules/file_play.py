import time
class FilePlay(object):

    def __init__(self,file):
        self.fh = open(file, "r")

    def next(self):
        line = None
        self.wait_count = 0

        # low CPU (probably same as the block below this, but ALLOWS tell()!
        while not line:
            line = self.fh.readline()
            time.sleep(0.002)
        return line
    def __next__(self):
        """Interator "next" call."""
        return self.next()