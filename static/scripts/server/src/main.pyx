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
    """
    process manager
    """
    cdef int8_t exitcode
    cdef str cmd
    def __init__(self, str cmd, on_write):
        # save on_write varable for sending output changes
        self.on_write = on_write
        self.cmd = cmd
        self.proc = None

    def run(self):
        """
        output checker system
        """
        # io variable for saving STDOUT & STDERR and communicate output event listener with output getter
        io = [b''] * 2

        def return_writes(io):
            """
            output event detector
            """
            res = b'' # res variable to save the sum of STDOUT and STDERR
            # save STDOUT value on res
            res += io[0]
            io[0] = b''
            # save STDERR value on res
            res += io[1]
            io[1] = b''
            if res != b'': # call on_write event if result is not empty
                self.on_write(res)

        def read(io):
            void_ret = [False] * 2 # void_ret for save STDOUT and STDERR is empty value for read full data

            # read STDOUT and STDERR
            while True:
                # iterate on readable outputs
                for out in select.select([self.proc.stdout, self.proc.stderr], [], [], 0.01)[0]:
                    while True:
                        loc_char = out.read(1) # read a character from output(STDOUT or STDERR)
                        # check process status and check output value for read all data after process close
                        if self.proc.poll() != None:
                            if out == self.proc.stdout:
                                if loc_char == b'':
                                    void_ret[0] = True
                            elif out == self.proc.stderr:
                                if loc_char == b'':
                                    void_ret[1] = True
                            break
                        # save STDOUT or STDERR data
                        if out == self.proc.stdout:
                            io[0] += loc_char
                        elif out == self.proc.stderr:
                            io[1] += loc_char
                # break loop if process closed and outputs getted
                if self.proc.poll() != None and void_ret[0] and void_ret[1]:
                    break
        # run output getter system as a thread
        threading.Thread(target=read, args=(io,)).start()

        # output event detector runner
        while self.proc.poll() == None: # run output event detector, while process not closed
            return_writes(io)
        return_writes(io) # run output event detector after process closed for return last data received
        
        self.exitcode = self.proc.poll() # get process exit code

    def start(self):
        """
        start process and output checker
        """
        self.proc = Popen(shlex.split(self.cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE) # open process
        threading.Thread(target=self.run).start() # run output checker system

    def write(self, data):
        """
        write data to STDIN of process
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def terminate(self):
        """
        send -15 signal to process (terminate that)
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        self.proc.terminate()

    def kill(self):
        """
        send -9 signal to process (kill that)
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        self.proc.kill()
    
    def wait(self):
        """
        wait to close process
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        self.proc.wait()
        
    def send_signal(self, int sig):
        """
        send any signal to process
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        self.proc.send_signal(sig)
        
    @property
    def pid(self):
        """
        pid of process (process id)
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() != None:
            raise Exception("process closed")
        return self.proc.pid
    
    @property
    def returncode(self):
        """
        process return code (exit code)
        """
        if self.proc == None:
            raise Exception("process not started")
        if self.proc.poll() == None:
            raise Exception("process is running")
        return self.exitcode


class PyProc(Process):
    pass


app = Flask(__name__)

@app.route("/")
def index():
    return "hello world!"