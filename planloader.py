#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import sys
import nose
import logging
import unittest
import ConfigParser
from functools import wraps
from multiprocessing import Process
from collections import  OrderedDict
#from nose.suite import *
from Queue import Queue, Empty
import threading

"""
module for loading test suite from config file and injecting timeout check in case method level.
"""

log = logging.getLogger(__name__)


def timeout(timeout=180):
    '''
    decorator for tiemout
    '''
    def func_wrapper(func):
        def arguments_wrapper(*args, **kwargs):
            q = Queue()
            _ = CaseThread(q, func, *args, **kwargs)
            _.setDaemon(True)
            _.start()
            try:
                error = q.get(timeout=timeout)
            except Empty:
                raise TimeoutException('timeout expired before end of test %f s' % timeout)
            if error is not None:
                exc_type, exc_value, tb = error
                raise exc_type, exc_value, tb
        return wraps(func)(arguments_wrapper)
    return func_wrapper

class TimeoutException(AssertionError):
    '''
    timeout exception
    '''
    def __init__(self, value = 'test Case Time Out'):
        self.value = value

    def __str__(self):
       return repr(self.value)

class LoadException(AssertionError):
    '''
    test suite load error
    '''
    def __init__(self, value = 'test suite load error'):
        self.value = value

    def __str__(self):
       return 'runner exited with loading test suite error:\n\t%s' % self.value

class CaseThread(threading.Thread):
    '''
    thread used to run test method
    '''
    def __init__(self, q=None , func=None, args=(), kwargs={}):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__q = q
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def run(self):
        try:
            self.__func(*self.__args, **self.__kwargs)
            self.__q.put(None)
        except:
            self.__q.put(sys.exc_info())

class PlanLoaderPlugin(nose.plugins.Plugin):
    '''
    test loader plugin. allow to specify a test plan file with format:
    [tests]
    packagename.modulename.classname.testName = 10
    packagename.modulename.classname.testName = 20 
    '''
    name = 'plan-loader'
    planfile = None

    def options(self, parser, env):
        '''
        Register commandline options.
        '''
        super(PlanLoaderPlugin, self).options(parser, env)
        parser.add_option('--plan-file', action='store', type='string', metavar="STRING",
                          dest='plan_file', default='plan',
                          help="Run the tests specified by the plan file")

        parser.add_option('--loop', action='store', type='string', metavar="STRING",
                          dest='loops', default='1',
                          help="Run the tests with specified loop number. default will execute forever")

        parser.add_option('--timeout', action='store', type='string', metavar="STRING",
                          dest='timeout', default='180',
                          help="the value of timeout for each test case method. 180 seconds as default")


    def configure(self, options, conf):
        '''
        Configure plugin.
        '''
        super(PlanLoaderPlugin, self).configure(options, conf)
        self.conf = conf
        self.loops = options.loops
        self.timeout = int(options.timeout)
        self.plan_file = os.path.expanduser(options.plan_file)
        if not os.path.isabs(self.plan_file):
            self.plan_file = os.path.join(conf.workingDir, self.plan_file)
        self.conf.workingDir = os.path.dirname(self.plan_file)
        if not os.path.exists(self.plan_file):
            raise Exception('file not found: %s' % self.plan_file)

    def prepareTestLoader(self, loader):
        '''
        Get handle on test loader so we can use it in loadTestsFromNames.
        '''
        self.loader = loader
        self.suiteClass = loader.suiteClass

    def __getTestsFromPlanFile(self, plan_file_path, section_name, cycle):
        '''
        load test sequence list from plan file 
        '''
        tests = []
        parser = ConfigParser.ConfigParser(dict_type=OrderedDict)
        parser.optionxform = lambda x: x
        parser.read(plan_file_path)
        tests = parser.items(section_name)
        n = 1
        while n <= int(cycle): 
            for (k,v) in tests:
                for i in range(int(v)):
                    yield k
            n += 1

    def loadTestsFromNames(self, names, module=None):
        '''
        replace the way of loading test case using plan file.
        '''
        names = self.__getTestsFromPlanFile(plan_file_path=self.plan_file, section_name='tests', cycle=self.loops)
        return (None, names)


    def loadTestsFromName(self, name, module=None, discovered=False):
        try:
            suites = unittest.TestLoader().loadTestsFromName(name, module)
        except Exception, e:
            exit(LoadException(e))
        self.__injectTimeout(suites)
        return suites

    def __injectTimeout(self, suites):
        for s in suites._tests:
            if not isinstance(s, unittest.suite.TestSuite):
                origin_m = getattr(s, s._testMethodName)
                wrapped_m = timeout(timeout=self.timeout)(origin_m)
                setattr(s, s._testMethodName, wrapped_m)
            else:
                self.__injectTimeout(s) 
