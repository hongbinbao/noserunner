#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import time
import shlex
import shutil
import signal
import logging
import threading
import traceback
import subprocess
import logging.handlers

'''
module used to call android/tizen platform debug bridge tool
'''

__all__ = ['AdbCommand', 'logger', 'logdeco']

FILE_LOG_LEVEL="DEBUG"
'''File Level'''

CONSOLE_LOG_LEVEL="INFO"
'''Console Level'''

LOCAL_TIME_STAMP_FORMAT = '%Y-%m-%d_%H:%M:%S'
'''local time format'''

REPORT_TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
'''report time format'''

LEVELS={"CRITICAL" :50,
        "ERROR" : 40,
        "WARNING" : 30,
        "INFO" : 20,
        "DEBUG" : 10,
        "NOTSET" :0,
       }
'''logger levels'''

def mkdir(path):
    '''
    create a folder
    @type path: string
    @param path: the path of folder
    @rtype: string
    @return: the path of the folder, return None if fail to create folder
    '''
    if os.path.exists(path):
        shutil.rmtree(path, onerror=forcerm)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def forcerm(fn, path, excinfo):
    '''
    force delete a folder
    @type path: string
    @param path: the path of folder
    @type excinfo: string
    @param excinfo: the output info when exception
    '''
    if fn is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif fn is os.remove:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

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

class Logger:
    '''
    class used to print log
    '''
    _instance=None
    _mutex=threading.Lock()

    def __init__(self, level="DEBUG"):
        '''
        constructor of Logger
        '''
        self._logger = logging.getLogger("NoseRunner")
        self._logger.setLevel(LEVELS[level])
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)
        self._formatter = logging.Formatter("[%(asctime)s] - %(levelname)s : %(message)s",'%Y-%m-%d %H:%M:%S')
        self._formatterc = logging.Formatter("%(message)s")
        self.add_file_logger()
        self.add_console_logger()

    def add_file_logger(self, log_file="./log/test.log", file_level="DEBUG"):
        '''
        generate file writer
        @type log_file: string
        @param log_file: the path of log file
        @type file_level: string
        @param file_level: the log output level.Defined in global LEVELS
        '''
        logFolder = 'log'
        mkdir(logFolder)
        if not os.path.exists(log_file):
            open(log_file,'w')
            
        fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=1024*1024*1,
                                                   backupCount=100,encoding="utf-8")
        fh.setLevel(LEVELS[file_level])
        fh.setFormatter(self._formatter)
        self._logger.addHandler(fh)

    def add_console_logger(self, console_level="INFO"):
        '''
        generate console writer
        @type console_level: string
        @param console_level: the level of console
        '''
        ch = logging.StreamHandler()
        ch.setLevel(LEVELS[console_level])
        ch.setFormatter(self._formatterc)
        self._logger.addHandler(ch)

    @staticmethod
    def getLogger(level="DEBUG"):
        '''
        return the logger instance
        @type level: string
        @param level: the level of logger
        @rtype: Logger
        @return: the instance of Logger      
        '''
        if(Logger._instance==None):
            Logger._mutex.acquire()
            if(Logger._instance==None):
                Logger._instance=Logger(level)
            else:
                pass
            Logger._mutex.release()
        else:
            pass
        return Logger._instance

    def debug(self, msg):
        '''
        print message for debug level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.debug(msg)

    def info(self, msg):
        '''
        print message for info level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.info(msg)

    def warning(self, msg):
        '''
        print message for warning level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.warning(msg)

    def error(self, msg):
        '''
        print message for error level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.error(msg)

    def critical(self, msg):
        '''
        print message for critical level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.critical(msg)

def logdeco(log=None, display_name=None):
    '''
    a wrapper that record the log of function or method and execution time silently and appends to a text file.
    @type log: Logger
    @param log: the instance of Logger
    @type display_name: string
    @param display_name: the display tag 
    '''
    if not log: log = logger
    #if not display_name: display_name = func.__name__
    def wrapper(func):
        def func_wrapper(*args, **kwargs):
            log.debug("enter func: %s" % func.__name__)
            for i, arg in enumerate(args):
                log.debug("\t arguments-%d: %s" % (i + 1, arg))
            for k, v in enumerate(kwargs):
                log.debug("\t dict arguments: %s: %s" % (k, v))
            ts = time.time()
            ret = func(*args, **kwargs)
            te = time.time()
            log.debug('%r (%r, %r) took %.3f seconds' % (func.__name__, args, kwargs, te-ts))
            log.debug("leave func: %s" % func.__name__)
            return ret
        return func_wrapper
    return wrapper

logger = Logger.getLogger()
'''single instance of logger'''

if __name__ == '__main__':
    print AdbCommand('adb devices', retry=2, timeout=5).run()