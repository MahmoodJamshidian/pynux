# distutils: language = c++
"""
Server & Process handler
Pynux branchs
"""

from flask import Flask
from subprocess import Popen, PIPE
from libcpp.string cimport string
from libc.stdint cimport int8_t
import threading
import select
import shlex


cdef class Process:
    cdef int8_t exitcode
    def __init__(self, str cmd, on_write):
        self.proc = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.on_write = on_write

    def run(self):
        io = [b''] * 2

        def return_writes(io):
            res = b''
            if io[0] != b'':
                res += io[0]
                io[0] = b''
            if io[1] != b'':
                res += io[1]
                io[1] = b''
            if res != b'':
                self.on_write(res)

        def read(io):
            void_ret = [False] * 2

            while True:
                for out in select.select([self.proc.stdout, self.proc.stderr], [], [], 0.01)[0]:
                    while True:
                        d = out.read(1)
                        if self.proc.poll() != None:
                            if out == self.proc.stdout:
                                if d == b'':
                                    void_ret[0] = True
                            elif out == self.proc.stderr:
                                if d == b'':
                                    void_ret[1] = True
                            break

                        if out == self.proc.stdout:
                            io[0] += d
                        elif out == self.proc.stderr:
                            io[1] += d
                if self.proc.poll() != None and void_ret[0] and void_ret[1]:
                    break

        threading.Thread(target=read, args=(io,)).start()

        res = b''
        while self.proc.poll() == None:
            return_writes(io)
        return_writes(io)
        
        self.exitcode = self.proc.poll()

    def start(self):
        threading.Thread(target=self.run).start()

    def write(self, data):
        self.proc.stdin.write(data)
        self.proc.stdin.flush()


app = Flask(__name__)

@app.route("/")
def index():
    return "hello world!"