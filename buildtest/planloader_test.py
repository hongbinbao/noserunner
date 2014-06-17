#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import unittest
from os.path import join, dirname
sys.path.append(dirname(dirname(__file__)))
import planloader


class PlanLoaderTest(unittest.TestCase):
    def setUp(self):
        self.m = getattr(planloader, 'readTestsFromConfigFile')
        self.plan = join(join(dirname(__file__),'resource'),'plan')
        self.repeat_plan = join(join(dirname(__file__),'resource'),'repeatplan')

    def testLoadNormalPlan(self):
        tests = self.m(self.plan, section='tests')
        self.assertEqual(tests[0][0] ,'sample.testcases.phone.Phone.testCall')
        self.assertEqual(tests[0][1] , 2)
        self.assertEqual(tests[1][0] ,'sample.testcases.browser.Browser.testOpenBrowser')
        self.assertEqual(tests[1][1] , 3)

    def testLoadRepeatPlan(self):
        tests = self.m(self.repeat_plan, section='tests')
        self.assertEqual(tests[0][0] , 'sample.testcases.phone.Phone.testCall')
        self.assertEqual(tests[0][1] , 2)
        self.assertEqual(tests[1][0] ,'sample.testcases.browser.Browser.testOpenBrowser')
        self.assertEqual(tests[1][1] , 2)
        self.assertEqual(tests[2][0] ,'sample.testcases.phone.Phone.testCall')
        self.assertEqual(tests[2][1] , 2)

    def tearDown(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PlanLoaderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)