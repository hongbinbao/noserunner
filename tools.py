#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import shlex
import signal
import threading
import traceback
import subprocess

'''
module used to call android/tizen platform debug bridge tool
'''

__all__ = ['AdbCommand']

class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.
    """
    command = None
    process = None
    status = None
    output, error = '', ''
 
    def __init__(self, command):
        if isinstance(command, basestring):
            command = shlex.split(command)
        self.command = command
 
    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.status = self.process.returncode
            except:
                self.error = traceback.format_exc()
                self.status = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE
        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.kill_proc(self.process.pid)
            thread.join()
        return self.status, self.output, self.error

    def kill_proc(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

class AdbCommand(Command):
    """
    run adb command in shell
    """
    def __init__(self, cmd, retry=3, timeout=10):
        Command.__init__(self, cmd)
        self.retry = retry
        self.timeout = timeout

    def run(self):
        output = None
        error = None
        status = -1
        while self.retry:
            status, output, error = Command.run(self, timeout=self.timeout, stderr=subprocess.STDOUT)
            if not status:
                return output
            else:
                self.retry -= 1
        if output:
        	raise Exception(str(output))
        elif error:
            raise Exception(str(error))


if __name__ == '__main__':
    print AdbCommand('adb devices', retry=2, timeout=5).run()