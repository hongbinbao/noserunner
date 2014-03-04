#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import sys
import time
import uuid
import json
import nose
import shutil
import zipfile
import logging
import datetime
import traceback
from ConfigParser import ConfigParser
from commands import getoutput as shell
from os.path import join, exists
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

def uniqueID():
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

def writeResultToFile(output, content):
    '''
    Used to generated brief result to local result.txt file.
    '''
    with open(output, 'a') as f:
        f.write('%s%s' % (json.dumps(content), os.linesep))

def formatOutput(name, etype, err):
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
    def __init__(self, sid=None, tid=0):
        self.__sid = sid if sid else uniqueID()
        self.__tid = tid

    @property
    def sid(self):
        '''
        return session id
        '''
        return self.__sid

    def next(self):
        '''
        generated test case id
        '''
        self.__tid += 1
        return self.__tid

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
    def case_report_dir_path(self):
        self.__case_report_dir_path = join(self.__output_failures, self.case_report_dir_name)
        return self.__case_report_dir_path

    @property
    def case_report_tmp_dir(self):
        self.__case_report_tmp_dir = join(join(os.getcwd(), 'tmp'), self.case_report_dir_name)
        #sys.stderr.write(self.__case_report_tmp_dir)
        return self.__case_report_tmp_dir

    @property
    def screenshot_at_failure(self):
        self.__screenshot_at_failure = join(self.case_report_dir_path, FAILURE_SNAPSHOT_NAME)
        return self.__screenshot_at_failure

    @property
    def log(self):
        self.__log = join(self.case_report_dir_path, 'log.zip')
        return self.__log

    @property
    def expect(self):
        return self.__expect

def zipLog(src, dest):
    import zipfile
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
                                                
    modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED:'stored'}                                                

    zf = zipfile.ZipFile(os.path.join(dest, 'log.zip'), mode='w')
    try:
        zf.write(src, compress_type=compression)
    finally:
        print 'closing'
        zf.close()

def save(path):
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
    #zipLog(os.path.join(path, LOG_FILE_NAME), path)


class ReporterPlugin(nose.plugins.Plugin):
    """
    Write test result to $WORKSPACE/result.txt or ./result.txt
    """
    name = 'reporter'
    #score = 200

    def __init__(self, counter=None, report_client=None):
        super(ReporterPlugin, self).__init__()
        self.__counter = counter if counter else TestCounter()
        self.__report_client = report_client if report_client else None

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
                          dest='directory', default=self.getDefault(),
                          help="save output file to this directory. default is current nose worspace")

        parser.add_option('--size', action='store',  metavar="FILE",
                          dest='server_config', default=4096,
                          help="file size limit")

        ###report server config###
        parser.add_option('--reportserver', action='store_true',
                          dest='reportserver', default=False,
                          help="switcher of uploading result to server. default is enable the feature")

        parser.add_option('--server-config', action='store',  metavar="FILE",
                          dest='server_config', default='server.config',
                          help="specify the server config file path")

    def getDefault(self):
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

    def _write(self, output):
        '''
        Write output as content
        '''
        try:
            self.stream.write(output)
        except:
            pass

    def begin(self):
        self.session_id = self.__counter.sid
        self.test_start_time = getattr(self, 'test_start_time', None)
        if not self.test_start_time:
            self.test_start_time = reporttime()
        self._report_path = _mkdir(join(join(self.opt.directory, 'report'), str(self.test_start_time).replace(' ', '_')))
        self._all_report_path = _mkdir(join(self._report_path, 'all'))
        self._fail_report_path = _mkdir(join(self._report_path, 'fail'))
        self._error_report_path = _mkdir(join(self._report_path, 'error'))
        self._timeout_report_path = _mkdir(join(self._report_path, 'timeout'))
        session_properties = {'sid': self.session_id,
                              'starttime': self.test_start_time
                              }
        if self.opt.reportserver and not self.__report_client.created:
            self.__report_client.createSession(**session_properties)

    def setTestCaseContext(self, test):
        module_name, class_name, method_name = test.id().split('.')[-3:]
        ctx = TestCaseContext(self._fail_report_path, self._error_report_path)
        ctx.case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        setattr(test.context, 'contexts', ctx)


    def getTestCaseContext(self, test):
        return getattr(test.context, 'contexts')

    def prepareTestCase(self, test):
        sys.stderr.write('------------------------------prepareTestCase-------------\n')
        self.setTestCaseContext(test)

    def startTest(self, test):
        """
        startTest: called after beforeTest(*)
        """
        self.tid = self.__counter.next()
        ctx = self.getTestCaseContext(test)
        ctx.case_start_time = reporttime()
        ctx.user_log_dir = join(ctx.case_report_tmp_dir, 'logs')
        if self.write_hashes:
            self._write('#%s %s ' % (str(self.tid), str(ctx.case_start_time)))

    def stopTest(self, test):
        """
        stopTest: called before afterTest(*)
        """
        pass

    def handleFailure(self, test, err):
        '''
        Called on addFailure. To handle the failure yourself and prevent normal failure processing, return a true value.
        '''
        self.result_properties.clear()
        exctype, value, tb = err

        ctx = self.getTestCaseContext(test)
        #common log output
        save(ctx.user_log_dir)
        shutil.move(ctx.case_report_tmp_dir, self._fail_report_path)

        self.result_properties.update({'extras': {'screenshot_at_failure': ctx.screenshot_at_failure,
                                                  'log': ctx.log,
                                                  'expect': ctx.expect,
                                                  }
                                      })

    def handleError(self, test, err):
        '''
        Called on addError. To handle the failure yourself and prevent normal error processing, return a true value.
        '''
        self.result_properties.clear()
        
        ctx = self.getTestCaseContext(test)
        #last step snapshot
        save(ctx.user_log_dir)
        shutil.move(ctx.case_report_tmp_dir, self._error_report_path)

        self.result_properties.update({'extras': {'screenshot_at_failure': ctx.screenshot_at_failure,
                                                  'log': ctx.log,
                                                  'expect': ctx.expect,
                                                 }
                                       })

    def addFailure(self, test, err, capt=None, tbinfo=None):
        ctx = self.getTestCaseContext(test)
        ctx.case_end_time = reporttime()
        #payload data
        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': ctx.case_dir_name,
                                                  'starttime': ctx.case_start_time,
                                                  'endtime': ctx.case_end_time,
                                                  'result': 'fail',
                                                  'trace':formatOutput(ctx.case_dir_name, 'fail', err)
                                                  }
                                       })
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addError(self, test, err, capt=None):
        ctx = self.getTestCaseContext(test)
        ctx.case_end_time = reporttime()

        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': ctx.case_dir_name,
                                                  'starttime': ctx.case_start_time,
                                                  'endtime': ctx.case_end_time,
                                                  'result': 'error',
                                                  'trace':formatOutput(ctx.case_dir_name, 'error', err)
                                                  }
                                       })

        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addSuccess(self, test, capt=None):
        ctx = self.getTestCaseContext(test)
        ctx.case_end_time = reporttime()
        self.result_properties.clear()
        self.result_properties.update({'payload': {'tid': self.tid,
                                                   'casename': ctx.case_dir_name,
                                                   'starttime': ctx.case_start_time,
                                                   'endtime': ctx.case_end_time,
                                                   'result': 'pass'
                                                  }
                                      })        
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)