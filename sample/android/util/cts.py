#!/usr/bin/python
# -*- coding:utf-8 -*- 
import unittest
import re, sys
from commands import getoutput as call

#standard way to launch instrumentation test case from command line
#am instrument -w -r -e class <class_name>#<method> -w <componment>
#example:
#am instrument -w -r -e class android.util.cts.XmlTest#testAsAttributeSet com.android.cts.util/android.test.InstrumentationCtsTestRunner
#am instrument -w -r -e class android.util.cts.XmlTest com.android.cts.util/android.test.InstrumentationCtsTestRunner
#am instrument -w com.android.cts.util/android.test.InstrumentationCtsTestRunner


def instrument(test):
    local_cmd = 'adb shell am instrument -w -r -e class %s#%s %s'
    #get the JAVA test class and method name by module path and name
    params = {'class': '%s.%s' % (test.__module__, type(test).__name__),
              'method': test._testMethodName,
              'componment':  test.inst_componment
              }

    cmd = local_cmd % (params['class'], params['method'], params['componment'])
    ret = call(cmd)
    vmap = {}
    result_tag = 'INSTRUMENTATION_RESULT: '  
    code_tag = 'INSTRUMENTATION_CODE'
    code_match = re.search(code_tag, ret)
    code_index = code_match.start()
    result_match = re.search(result_tag, ret)
    results = ret[result_match.end(): code_index].strip().replace('\r\n', ' ')
    index = results.index('=')
    key = results[0: index]
    value = results[(index+1):]
    vmap[key] = value
    return vmap

class XmlTest(unittest.TestCase):

    def setUp(self):
        super(XmlTest, self).setUp()
        self.inst_componment = 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'

    def tearDown(self):
        super(XmlTest, self).tearDown()

    def testAsAttributeSet(self):
        #yield instrument, inst_params
        output = instrument(self)
        assert output['stream'].find('OK') != -1, ret

    def testFindEncodingByName(self):
        #yield instrument, inst_params
        output = instrument(self)
        assert output['stream'].find('OK') != -1, ret

