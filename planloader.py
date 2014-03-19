#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os
import sys
import logging
import unittest
import ConfigParser
from collections import  OrderedDict
import nose
from nose.suite import *
log = logging.getLogger(__name__)

class PlanLoaderPlugin(nose.plugins.Plugin):
    """
    test loader plugin. allow to specify a test plan file with format:
    [tests]
    packagename.modulename.classname.testName = 10
    packagename.modulename.classname.testName = 20 
    """
    name = 'plan-loader'
    planfile = None

    def options(self, parser, env):
        """Register commandline options.
        """
        super(PlanLoaderPlugin, self).options(parser, env)
        parser.add_option('--plan-file', action='store', type='string',metavar="STRING",
                          dest='plan_file', default='plan',
                          help="Run the tests that list in plan file")

        parser.add_option('--loop', action='store', type='string',metavar="STRING",
                          dest='loops', default='1',
                          help="Run the tests with specified loop number. default will execute forever ")


    def configure(self, options, conf):
        """Configure plugin.
        """
        super(PlanLoaderPlugin, self).configure(options, conf)
        if not self.enabled:
            return
        #print options
        #if options.stability_test_loader:
        #    self.enabled = True
        self.conf = conf
        if options.plan_file:
            self.enabled = True
        if options.loops:
            self.enabled = True
            self.loops = options.loops
        self.plan_file = os.path.expanduser(options.plan_file)
        if not os.path.isabs(self.plan_file):
            self.plan_file = os.path.join(conf.workingDir, self.plan_file)
        self.conf.workingDir = os.path.dirname(self.plan_file)
        if not os.path.exists(self.plan_file):
            raise Exception('file not found: %s' % self.plan_file)

    def prepareTestLoader(self, loader):
        """
        Get handle on test loader so we can use it in loadTestsFromNames.
        """
        self.loader = loader
        self.suiteClass = loader.suiteClass

    def getTestsFromPlanFile(self, plan_file_path, section_name, cycle):
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
        """
        replace the way of loading test case using plan file.
        """
        loader = self.loader
        names = self.getTestsFromPlanFile(plan_file_path=self.plan_file, section_name='tests', cycle=self.loops)
        return (None, names)


    def loadTestsFromName(self, name, module=None, discovered=False):
        #unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: cmp(y, x)
        return unittest.TestLoader().loadTestsFromName(name, module)

