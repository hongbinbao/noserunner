#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, os
import unittest
from os.path import join, dirname
sys.path.append('..')
from noserunner import reporter


class ReporterTest(unittest.TestCase):
    def setUp(self):
        pass

    def testLoadServerConfiguration(self):
        server_config = join(join(dirname(__file__),'resource'),'livereport.config')
        info = reporter._getServerConfiguration(server_config)
        self.assertEqual(info['username'],'test')
        self.assertEqual(info['password'],'123456')
        self.assertEqual(info['session_create'],'http://domain:port/api/session_create')
        self.assertEqual(info['session_update'],'http://domain:port/api/session_update')
        self.assertEqual(info['case_update'],'http://domain:port/api/case_update')
        self.assertEqual(info['file_upload'],'http://domain:port/api/file_upload')      

    def testLoadDeviceConfiguration(self):
        device_config = join(join(dirname(__file__),'resource'),'device.config')
        info = reporter._getDeviceConfiguration(device_config)
        self.assertEqual(info['product'],'product_name')
        self.assertEqual(info['revision'],'revision_number')
        self.assertEqual(info['deviceid'],'0123456789ABCDEF')
        self.assertEqual(info['screen_width'],'800')
        self.assertEqual(info['screen_height'],'1024')

    def testGetAdbLocation(self):
        adb = reporter._findExetuable('adb')
        self.assertTrue(os.path.exists(adb), 'adb not found on environment PATH')

    def tearDown(self):
        pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ReporterTest)
    unittest.TextTestRunner(verbosity=2).run(suite)