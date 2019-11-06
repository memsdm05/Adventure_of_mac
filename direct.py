# UNUSED CODE
# DOES NOT DO ANYTHING

import subprocess
import os


class Yeet:
    def __init__(self):
        self.out = {}


    def parse(self):
        self.result = subprocess.run('ls -op'.split(), stdout=subprocess.PIPE)
        self.formatted = self.result.stdout.decode('utf-8').split('\n')

        for i in self.formatted[1:len(self.formatted)-1]:
            self.temp = i.split()
            del self.temp[0:3]
            del self.temp[1:4]
            del self.temp[2:]
            self.out[self.temp[1]] = self.temp[0]

    def keys(self):
        for i in self.out.keys():
            print(i)


