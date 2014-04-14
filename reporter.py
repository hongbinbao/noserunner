#!/usr/bin/python
# -*- coding:utf-8 -*- 


import os
import sys
import shlex
import time
import uuid
import json
import nose
import time
import Queue
import signal
import string
import shutil
import zipfile
import logging
import datetime
import datetime
import traceback
import subprocess
import threading
from ConfigParser import ConfigParser
from commands import getoutput as shell
from os.path import join, exists, dirname
from client import ReportClient


log = logging.getLogger(__name__)
'''global log instance'''

TAG='%s%s%s' % ('-' * 18, 'file output save Plugin', '-' * 18)
'''global log output tag'''

TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
'''global time stamp format'''

OUTPUT_FILE_NAME = 'result.txt'
'''global test result output file name'''

LOG_FILE_NAME = 'log.txt'
'''global test log output name'''

FAILURE_SNAPSHOT_NAME = 'failure.png'
'''default string name of result file. can be modify by user-specify'''

REPORT_TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

ANDROID_LOG_SHELL = 'adb %s %s logcat -v time'
'''android log shell command line'''

def _uniqueID():
    '''
    return a unique id of test session.
    '''
    return str(uuid.uuid1())

def _time():
    '''
    generic time stamp format
    '''
    #return time.strftime(TIME_STAMP_FORMAT, time.localtime(time.time()))
    return str(datetime.datetime.now())

def reporttime():
    '''
    return time stamp format with REPORT_TIME_STAMP_FORMAT
    '''
    return time.strftime(REPORT_TIME_STAMP_FORMAT, time.localtime(time.time()))

def _mkdir(path):
    '''
    create directory as path
    '''
    if not exists(path):
        os.makedirs(path)
    return path

def _writeResultToFile(output, content):
    '''
    Used to generated brief result to local result.txt file.
    '''
    with open(output, 'a') as f:
        f.write('%s%s' % (json.dumps(content), os.linesep))

def _formatOutput(name, etype, err):
    '''
    change the output format of exception
    '''
    exception_text = traceback.format_exception(*err)
    #exception_text = "".join(exception_text).replace(os.linesep, '')
    return exception_text

class TestCounter(object):
    '''
    Test session counter.
    '''
    def __init__(self, sid=None, tid=0, cid=0, cycles=None):
        self.__sid = sid if sid else _uniqueID()
        self.__tid = tid
        self.__cid = cid
        self.__total_cycle = cycles

    @property
    def sid(self):
        '''
        return session id
        '''
        return self.__sid

    def next_tid(self):
        '''
        generated test case id
        '''
        self.__tid += 1
        return self.__tid

    def next_cid(self):
        '''
        generated test case id
        '''
        self.__cid += 1
        return self.__cid

    def progress(self):
        if self.__total_cycle:
            #return '%.0f%%' % (100.0 * self.__cid/int(self.__total_cycle))
            return '%0.2f' % (float(self.__cid)/float(self.__total_cycle))
        else:
            return 'unkown'

    def alive(self):
        if int(self.__cid) == int(self.__total_cycle):
            return False
        else:
            return True

    def total(self):
        '''
        return the number of test case
        '''
        return self.__tid

    def reset(self):
        '''
        reset test case id
        '''
        self.__tid = 0

class TestCaseContext(object):
    '''
    Test case context. test case extends from unittest.TestCase can refer it by self.contexts.
    The instance of it is injected to the context of test case instance by plugin when prepareTestCase.
    
    '''
    def __init__(self, output_failures, output_errors):
        self.__output_failures = output_failures
        self.__output_errors = output_errors
        self.__case_start_time = None
        self.__case_end_time = None
        self.__case_dir_name = None
        self.__user_log_dir = None
        self.__case_report_dir_name = None
        self.__case_report_dir_path = None
        self.__case_report_tmp_dir = None
        self.__screenshot_at_failure = None
        self.__log = None
        self.__expect = None

    @property
    def case_start_time(self):
        return self.__case_start_time

    @case_start_time.setter
    def case_start_time(self, v):
        self.__case_start_time = v

    @property
    def case_end_time(self):
        return self.__case_end_time

    @case_end_time.setter
    def case_end_time(self, v):
        self.__case_end_time = v

    @property
    def user_log_dir(self):
        return self.__user_log_dir

    @user_log_dir.setter
    def user_log_dir(self, v):
        self.__user_log_dir = v

    @property
    def case_dir_name(self):
        return self.__case_dir_name

    @case_dir_name.setter
    def case_dir_name(self, v):
        self.__case_dir_name = v

    ###
    @property
    def case_report_dir_name(self):
        self.__case_report_dir_name = '%s%s%s' % (self.__case_dir_name, '@', str(self.__case_start_time).replace(' ', '_'))
        return self.__case_report_dir_name

    #nose frm need
    @property
    def fail_case_report_dir_path(self):
        self.__case_report_dir_path = join(self.__output_failures, self.case_report_dir_name)
        return self.__case_report_dir_path

    @property
    def error_case_report_dir_path(self):
        self.__case_report_dir_path = join(self.__output_errors, self.case_report_dir_name)
        return self.__case_report_dir_path

    @property
    def case_report_tmp_dir(self):
        self.__case_report_tmp_dir = join(join(os.getcwd(), 'tmp'), self.case_report_dir_name)
        return self.__case_report_tmp_dir

    @property
    def fail_screenshot_at_failure(self):
        self.__screenshot_at_failure = join(join(self.fail_case_report_dir_path, 'logs'), FAILURE_SNAPSHOT_NAME)
        return self.__screenshot_at_failure

    @property
    def fail_log(self):
        self.__log = join(self.fail_case_report_dir_path, 'log.zip')
        return self.__log

    @property
    def error_screenshot_at_failure(self):
        self.__screenshot_at_failure = join(join(self.error_case_report_dir_path, 'logs'), FAILURE_SNAPSHOT_NAME)
        return self.__screenshot_at_failure

    @property
    def error_log(self):
        self.__log = join(self.error_case_report_dir_path, 'log.zip')
        return self.__log

    @property
    def expect(self):
        return self.__expect

def _zipFolder(folder_name, file_name, includeEmptyDIr=False):
    '''
    create a zip file for folder
    '''
    empty_dirs = []
    try:  
        ziper = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)  
        for root, dirs, files in os.walk(folder_name):
            empty_dirs.extend([d for d in dirs if os.listdir(os.path.join(root, d)) == []])  
            for name in files:
                ziper.write(os.path.join(root ,name), name)
                #fix same name error
                #full zip with parent dir
                #ziper.write(os.path.join(root ,name), os.path.join(os.path.splitext(filename)[0],name))
            if includeEmptyDIr:  
                for d in empty_dirs:  
                    zif = zipfile.ZipInfo(os.path.join(root, d) + "/")  
                    ziper.writestr(zif, "")
            empty_dirs = []
        return True
    except:
        return False
    finally:
        if ziper != None:
            ziper.close()

def _grabLog(path):
    '''
    pull log/snapshot from device to local report folder
    '''
    path = _mkdir(path)
    serial = os.environ['ANDROID_SERIAL'] if os.environ.has_key('ANDROID_SERIAL') else None
    #snapshot & system log
    if serial:
        shell('adb -s %s shell screencap /sdcard/%s' % (serial, FAILURE_SNAPSHOT_NAME))
        shell('adb -s %s pull /sdcard/%s %s' % (serial, FAILURE_SNAPSHOT_NAME, path))
        shell('adb -s %s logcat -v time -d > %s ' % (serial, join(path, LOG_FILE_NAME)))
    else:
        shell('adb shell screencap /sdcard/%s' % FAILURE_SNAPSHOT_NAME)
        shell('adb pull /sdcard/%s %s' % (FAILURE_SNAPSHOT_NAME, path))
        shell('adb logcat -v time -d > %s ' % join(path, LOG_FILE_NAME))
    _zipFolder(join(dirname(path), 'logs'), join(dirname(path), 'log.zip'))

def _makeLog(path, result='failure'):
    '''
    pull log/snapshot from device to local report folder
    '''
    path = _mkdir(path)
    snapshot_name = '%s%s%s' % (result, '.', 'png')
    serial = os.environ['ANDROID_SERIAL'] if os.environ.has_key('ANDROID_SERIAL') else None
    #snapshot & system log
    if serial:
        shell('adb -s %s shell screencap /sdcard/%s' % (serial, snapshot_name))
        shell('adb -s %s pull /sdcard/%s %s' % (serial, snapshot_name, path))
    else:
        shell('adb shell screencap /sdcard/%s' % snapshot_name)
        shell('adb pull /sdcard/%s %s' % (snapshot_name, path))
    _zipFolder(join(dirname(path), 'logs'), join(dirname(path), 'log.zip'))


class Timer(object):
    def __init__(self, duration):
        self.__starttime = datetime.datetime.now()
        self.__duration = duration

    def alive(self):
        isAlive = (datetime.datetime.now() - self.__starttime) < self.__duration
        return  isAlive

    def progress(self):
        #return "{:.2%}".format((datetime.datetime.now() - self.__starttime).total_seconds()/self.__duration.total_seconds())
        p = '%0.2f' % (float((datetime.datetime.now() - self.__starttime).total_seconds())/(self.__duration.total_seconds()))
        if float(p) <= float(0):
            return '0.01'
        if float(p) > float(1.0):
            return '1.00'
        else: return p
        #return '%0.02f' % (float((datetime.datetime.now() - self.__starttime).total_seconds())/(self.__duration.total_seconds()))

class LogHandler(object):
    def __init__(self, cmd):
        self.__cmd = cmd
        self.__cache_queue = Queue.Queue()
        self.__logger_proc = None
        self.__cache_thread = None
        
    def start(self):
        cmd = None
        serial = os.environ['ANDROID_SERIAL'] if os.environ.has_key('ANDROID_SERIAL') else None
        if serial:
            cmd = ANDROID_LOG_SHELL % ('-s', serial)
        else:
            cmd = ANDROID_LOG_SHELL % ('', '')
        self.__logger_proc = subprocess.Popen(shlex.split(cmd),\
                                              stdout=subprocess.PIPE,\
                                              close_fds=True,\
                                              preexec_fn=self.check)
        self.__cache_thread = LogCacheWrapper(self.__logger_proc.stdout, self.__cache_queue)
        self.__cache_thread.start()


    def stop(self):
        if self.__cache_thread:
            try:
                self.__cache_thread.stop()
            except: pass
        if self.__logger_proc:
            try:
                self.__logger_proc.kill()
            except: pass

    def check(self):
        pass

    def available(self):
        if not self.__logger_proc or not self.__cache_thread:
            return False
        return self.__cache_thread.is_alive() and not self.__logger_proc.poll()

    def save(self, path):
        with open(path, 'w+') as f:
            while self.__cache_queue.qsize() <= 0:
                time.sleep(1)
                continue
            for i in range(self.__cache_queue.qsize()):
               line = self.__cache_queue.get(block=True)
               f.write(line)

    def drop(self):
        self.__cache_queue.queue.clear()
            

class LogCacheWrapper(threading.Thread):
    def __init__(self, fd, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__fd = fd
        self.__queue = queue
        self.__stop = False

    def stop(self):
        self.__stop = True

    def run(self):
        for line in iter(self.__fd.readline, ''):
            self.__queue.put(line)

class ReporterPlugin(nose.plugins.Plugin):
    """
    handle test output.
    """
    name = 'reporter'
    #score = 200

    def __init__(self, counter=None, report_client=None, timer=None):
        super(ReporterPlugin, self).__init__()
        self.__report_client = report_client if report_client else None
        self.__counter = counter
        self.__timer = timer
        self.__log_handler = LogHandler(ANDROID_LOG_SHELL)

    def options(self, parser, env):
        """ 
        Register commandline options.
        Called to allow plugin to register command line options with the parser. DO NOT return a value from this method unless you want to stop all other plugins from setting their options.        
        """
        super(ReporterPlugin, self).options(parser, env)

        ###local ouput result config###
        parser.add_option('--file-name', 
                          dest='file_name', default='result.txt',
                          help="save output file to this directory")

        parser.add_option('--directory', action='store_true',
                          dest='directory', default=self.__getDefault(),
                          help="save output file to this directory. default is current nose worspace")

        parser.add_option('--icycle', action='store', type='string',metavar="STRING",
                          dest='icycle', default=None, help="total cycle flag")

        ###report server config###
        parser.add_option('--reportserver', action='store_true',
                          dest='reportserver', default=False,
                          help="switcher of uploading result to server. default is enable the feature")

        parser.add_option('--server-config', action='store',  metavar="FILE",
                          dest='server_config', default='server.config',
                          help="specify the server config file path")

        parser.add_option('--duration', dest='duration', type='string',metavar="STRING",
                          action='callback', callback=self.__validate_duration, 
                          help='The minumum test duration before ending the test.\
                                  Here format must follow next format: xxDxxHxxMxxS.\
                                  e.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds')

    def __validate_duration(self, option, opt, value, parser):
        '''
        '''
        value = string.lower(value)
        begin = 0
        days = hours = minutes = seconds = 0
        for i, v in enumerate(value):
            if v == 'd':
                days = int(value[begin:i])
                begin = i + 1
            elif v == 'h':
                hours = int(value[begin:i])
                begin = i + 1
            elif v == 'm':
                minutes = int(value[begin:i])
                begin = i + 1
            elif v == 's':
                seconds = int(value[begin:i])
                begin = i + 1
        if begin == 0:
            parser.error('%s: duration format error' % value) 
        times = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)      
        setattr(parser.values, option.dest, times)

    def __getDefault(self):
        workspace = os.getcwd()
        if 'WORKSPACE' in os.environ:
            ws = os.environ['WORKSPACE']
            workspace = _mkdir(ws)
        return workspace

    def configure(self, options, conf):
        """
        Called after the command  line has been parsed, with the parsed options and the config container. Here, implement any config storage or changes to state or operation that are set by command line options. DO NOT return a value from this method unless you want to stop all other plugins from being configured.
        """
        super(ReporterPlugin, self).configure(options, conf)
        if not self.enabled: return

        self.write_hashes = conf.verbosity == 2
        self.conf = conf
        self.opt = options

        if self.opt.icycle and not self.__counter:
            self.__counter = TestCounter(cycles=self.opt.icycle)
        elif not self.__counter:
            self.__counter = TestCounter()

        if self.opt.duration and not self.__timer:
            self.__timer = Timer(self.opt.duration)

        self.result_properties = {'payload': None, 'extras': None}
        #if disable report server
        if self.opt.reportserver and not self.__report_client:
            server_need = {'username':None, 'password':None, 'auth':None, 'session_create':None,
                           'session_update':None, 'case_create':None, 'case_update':None, 'file_upload':None}
            if not exists(options.server_config):
                raise Exception('exit due to unable to find server config file!')
            self.__report_client =  ReportClient(config=options.server_config)
            self.token = self.__report_client.regist()
            if not self.token:
                raise Exception('exit due to unable to get token from server!')

        #used to add local report if need
        #self.result_file = join(_mkdir(self.opt.directory), self.opt.file_name)

    def setOutputStream(self, stream):
        """
        Get handle on output stream so the plugin can print id #n
        """
        self.stream = stream

    def __write(self, output):
        '''
        Write output as content
        '''
        try:
            self.stream.write(output)
        except:
            pass

    def prepareTest(self, test):
        '''
        enable log handler.
        '''
        if not self.__log_handler.available():
            self.__log_handler.start()

    def begin(self):
        self.session_id = self.__counter.sid  
        self.test_start_time = getattr(self, 'test_start_time', None)
        if not self.test_start_time:
            self.test_start_time = reporttime()
        self.opt.directory = self.conf.workingDir
        self._report_path = _mkdir(join(join(self.opt.directory, 'report'), str(self.test_start_time).replace(' ', '_')))
        self._pass_report_path = _mkdir(join(self._report_path, 'pass'))
        self._fail_report_path = _mkdir(join(self._report_path, 'fail'))
        self._error_report_path = _mkdir(join(self._report_path, 'error'))
        self._timeout_report_path = _mkdir(join(self._report_path, 'timeout'))
        session_properties = {'sid': self.session_id,
                              'starttime': self.test_start_time
                              }
        self.cid = self.__counter.next_cid()
        if self.write_hashes:
            sys.stderr.write('begin cycle: %s \n' % (self.cid))                          
        if self.opt.reportserver and not self.__report_client.created:
            self.__report_client.createSession(**session_properties)

    def __setTestCaseContext(self, test):
        module_name, class_name, method_name = test.id().split('.')[-3:]
        ctx = TestCaseContext(self._fail_report_path, self._error_report_path)
        ctx.case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        setattr(test.context, 'contexts', ctx)

    def __getTestCaseContext(self, test):
        return getattr(test.context, 'contexts')

    def prepareTestCase(self, test):
        self.__setTestCaseContext(test)

    def startTest(self, test):
        """
        startTest: called after beforeTest(*)
        """
        self.tid = self.__counter.next_tid()
        ctx = self.__getTestCaseContext(test)
        ctx.case_start_time = reporttime()
        ctx.user_log_dir = join(ctx.case_report_tmp_dir, 'logs')
        path = _mkdir(ctx.user_log_dir)

        if self.write_hashes:
            self.__write('#%s %s ' % (str(self.tid), str(ctx.case_start_time)))


    def handleFailure(self, test, err):
        '''
        Called on addFailure. To handle the failure yourself and prevent normal failure processing, return a true value.
        '''
        self.result_properties.clear()
        exctype, value, tb = err

        try:
            ctx = self.__getTestCaseContext(test)
            log_file = join(ctx.user_log_dir, LOG_FILE_NAME)
            self.__log_handler.save(log_file)
            #makeLog(ctx.user_log_dir)
            #shutil.move(ctx.case_report_tmp_dir, self._fail_report_path)
        except:
            pass

        self.result_properties.update({'extras': {'screenshot_at_failure': ctx.fail_screenshot_at_failure,
                                                  'log': ctx.fail_log,
                                                  'expect': ctx.expect,
                                                  }
                                      })

    def handleError(self, test, err):
        '''
        Called on addError. To handle the failure yourself and prevent normal error processing, return a true value.
        '''
        self.result_properties.clear()
        
        try:
            ctx = self.__getTestCaseContext(test)
            log_file = join(ctx.user_log_dir, LOG_FILE_NAME)
            self.__log_handler.save(log_file)
            #makeLog(ctx.user_log_dir)
        except:
            pass

        self.result_properties.update({'extras': {'screenshot_at_failure': ctx.error_screenshot_at_failure,
                                                  'log': ctx.error_log,
                                                  'expect': ctx.expect,
                                                 }
                                       })

    def addFailure(self, test, err, capt=None, tbinfo=None):
        ctx = self.__getTestCaseContext(test)
        ctx.case_end_time = reporttime()
        #payload data
        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': ctx.case_dir_name,
                                                  'starttime': ctx.case_start_time,
                                                  'endtime': ctx.case_end_time,
                                                  'result': 'fail',
                                                  'trace':_formatOutput(ctx.case_dir_name, 'fail', err)
                                                  }
                                       })
        trace_log_path = join(ctx.user_log_dir, 'trace.txt')
        with open(trace_log_path, 'w+') as f:
            f.write(str(self.result_properties['payload']['trace']))
        _makeLog(ctx.user_log_dir)
        try:
            shutil.move(ctx.case_report_tmp_dir, self._fail_report_path)
        except:
            pass
        if self.__timer and not self.__timer.alive():
            self.conf.stopOnError = True
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addError(self, test, err, capt=None):
        ctx = self.__getTestCaseContext(test)
        ctx.case_end_time = reporttime()

        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': ctx.case_dir_name,
                                                  'starttime': ctx.case_start_time,
                                                  'endtime': ctx.case_end_time,
                                                  'result': 'error',
                                                  'trace':_formatOutput(ctx.case_dir_name, 'error', err)
                                                  }
                                       })
        trace_log_path = join(ctx.user_log_dir, 'trace.txt')
        with open(trace_log_path, 'w+') as f:
            f.write(str(self.result_properties['payload']['trace']))
        _makeLog(ctx.user_log_dir)
        try:
            shutil.move(ctx.case_report_tmp_dir, self._error_report_path)
        except:
            pass
        if self.__timer and not self.__timer.alive():
            self.conf.stopOnError = True

        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addSuccess(self, test, capt=None):
        ctx = self.__getTestCaseContext(test)
        ctx.case_end_time = reporttime()
        self.result_properties.clear()
        self.result_properties.update({'payload': {'tid': self.tid,
                                                   'casename': ctx.case_dir_name,
                                                   'starttime': ctx.case_start_time,
                                                   'endtime': ctx.case_end_time,
                                                   'result': 'pass'
                                                  }
                                      })
        #self.__log_handler.drop()
        log_file = join(ctx.user_log_dir, LOG_FILE_NAME)
        self.__log_handler.save(log_file)
        trace_log_path = join(ctx.user_log_dir, 'trace.txt')
        with open(trace_log_path, 'w+') as f:
            f.write(str(self.result_properties['payload']['result']))
        _makeLog(ctx.user_log_dir, 'pass')
        try:
            shutil.move(ctx.case_report_tmp_dir, self._pass_report_path)
        except:
            pass
        if self.__timer and not self.__timer.alive():
            self.conf.stopOnError = True
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    def report(self, stream):
        session_properties = {'sid': self.session_id}
        if self.opt.duration and self.__timer:
            session_properties.update({'status': self.__timer.progress()})
        elif self.opt.icycle and self.__counter:
            session_properties.update({'status': self.__counter.progress()})
        if self.opt.reportserver:
            self.__report_client.updateSession(**session_properties)                            
        return None

    def finalize(self, result):
        if self.write_hashes:
            self.__write('end cycle: %s \n' % (self.cid)) 
        session_properties = {'sid': self.session_id}
        if self.opt.icycle and not self.__counter.alive() and self.opt.reportserver:
            session_properties.update({'endtime': reporttime()})
            self.__report_client.updateSession(**session_properties)
        if self.conf.stopOnError and self.opt.reportserver:
            session_properties.update({'endtime': reporttime()})
            self.__report_client.updateSession(**session_properties)
            sys.exit(1)
        return None
