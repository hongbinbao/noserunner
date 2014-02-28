#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import sys
import time
import logging
import shutil
import nose
from commands import getoutput as shell
from os.path import join, exists
import json
from StringIO import StringIO as p_StringO
from cStringIO import OutputType as c_StringO
import traceback
import datetime
import uuid
from ConfigParser import ConfigParser
from client import ReportClient
import zipfile
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
#WORDINGDIR = os.environ['WORKSPACE'],
'''default output workspace'''
#SIZE_OF_FILE = 4096
'''default size of result file'''
REPORT_TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


class TestCounter(object):
    '''
    Test Session counter.
    '''
    def __init__(self, sid=None, tid=0):
        self.__sid = sid if sid else uniqueID()
        self.__tid = tid

    @property
    def sid(self):
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
        self.__tid = 0

def uniqueID():
    return str(uuid.uuid1())

def _time():
    '''
    time stamp format
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
    zipLog(os.path.join(path, LOG_FILE_NAME), path)

def writeResultToFile(output, content):
    '''
    Used to generated brief result to local result.txt file.
    '''
    with open(output, 'a') as f:
        f.write('%s%s' % (json.dumps(content), os.linesep))

def formatOutput(name, etype, err):
    exception_text = traceback.format_exception(*err)
    #exception_text = "".join(exception_text).replace(os.linesep, '')
    return exception_text

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
            #self.test_start_time = str(datetime.datetime.now())
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

    def startTest(self, test):
        """
        startTest: called after beforeTest(*)
        """
        self.tid = self.__counter.next()
        ##self.case_start_time = str(datetime.datetime.now())
        self.case_start_time = reporttime()
        if self.write_hashes:
            self._write('#%s %s ' % (str(self.tid), str(self.case_start_time)))


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

        module_name = test.id().split('.')[-3]
        class_name = test.id().split('.')[-2]
        method_name = test.id().split('.')[-1]
        case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        case_start_time = self.case_start_time
        case_report_dir_name = '%s%s%s' % (case_dir_name, '@', str(self.case_start_time).replace(' ', '_'))
        case_report_dir_path = join(self._fail_report_path, case_report_dir_name)
        screenshot_at_failure = None
        log = None
        expect = None

        if False:
            screenshot_at_failure = None
            log = None
            expect = None
        else:
            tmp = join(os.getcwd(), 'tmp')
            case_report_dir = _mkdir(join(tmp, case_report_dir_name))
            #last step snapshot
            save(case_report_dir)
            try:
                shutil.move(case_report_dir, self._fail_report_path)
            except:
                #if fail again
                pass
            screenshot_at_failure = join(case_report_dir_path, FAILURE_SNAPSHOT_NAME)
            log = join(case_report_dir_path, 'log.zip')

        self.result_properties.update({'extras': {'screenshot_at_failure': screenshot_at_failure,
                                                  'log': log,
                                                  'expect': expect,
                                                  }
                                      })

    def handleError(self, test, err):
        '''
        Called on addError. To handle the failure yourself and prevent normal error processing, return a true value.
        '''
        self.result_properties.clear()
        exctype, value, tb = err
        module_name = test.id().split('.')[-3]
        class_name = test.id().split('.')[-2]
        method_name = test.id().split('.')[-1]
        case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        case_start_time = self.case_start_time
        case_report_dir_name = '%s%s%s' % (case_dir_name, '@', str(self.case_start_time).replace(' ', '_'))
        case_report_dir_path = join(self._error_report_path, case_report_dir_name)

        screenshot_at_failure = None
        log = None
        expect = None

        if False:
            screenshot_at_failure = None
            log = None
            expect = None
        else:
            tmp = join(os.getcwd(), 'tmp')
            case_report_dir = _mkdir(join(tmp, case_report_dir_name))
            #last step snapshot
            save(case_report_dir)
            try:
                shutil.move(case_report_dir, self._error_report_path)
            except:
                #if error again
                pass
            screenshot_at_failure = join(case_report_dir_path, FAILURE_SNAPSHOT_NAME)
            log = join(case_report_dir_path, 'log.zip')
            expect = None

        self.result_properties.update({'extras': {'screenshot_at_failure': screenshot_at_failure,
                                                  'log': log,
                                                  'expect': expect,
                                                 }
                                       })

    def addFailure(self, test, err, capt=None, tbinfo=None):
        module_name = test.id().split('.')[-3]
        class_name = test.id().split('.')[-2]
        method_name = test.id().split('.')[-1]
        case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        #payload data
        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': case_dir_name,
                                                  'starttime': self.case_start_time,
                                                  'endtime': reporttime(),
                                                  'result': 'fail',
                                                  'trace':formatOutput(case_dir_name, 'fail', err)
                                                  }
                                       })
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addError(self, test, err, capt=None):
        module_name = test.id().split('.')[-3]
        class_name = test.id().split('.')[-2]
        method_name = test.id().split('.')[-1]
        case_dir_name = '%s%s%s' % (class_name, '.', method_name)
        case_start_time = self.case_start_time

        self.result_properties.update({'payload': {'tid': self.tid,
                                                  'casename': case_dir_name,
                                                  'starttime': self.case_start_time,
                                                  'endtime': reporttime(),
                                                  'result': 'error',
                                                  'trace':formatOutput(case_dir_name, 'error', err)
                                                  }
                                       })

        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)

    #remote upload
    def addSuccess(self, test, capt=None):
        module_name = test.id().split('.')[-3]
        class_name = test.id().split('.')[-2]
        method_name = test.id().split('.')[-1]
        case_dir_name = '%s%s%s' % (class_name, '.', method_name)

        self.result_properties.clear()
        self.result_properties.update({'payload': {'tid': self.tid,
                                                   'casename': case_dir_name,
                                                   'starttime': self.case_start_time,
                                                   'endtime': reporttime(),
                                                   'result': 'pass'
                                                  }
                                      })        
        if self.opt.reportserver:
            self.__report_client.updateTestCase(**self.result_properties)
