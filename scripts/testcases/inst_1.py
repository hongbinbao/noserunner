#!/usr/bin/python
# -*- coding:utf-8 -*- 
import unittest
import re
from commands import getoutput as call

#standard way to launch instrumentation test case from command line
#am instrument -w -r -e class <class_name>#<method> -w <componment>
#example:
#am instrument -w -r -e class android.util.cts.XmlTest#testAsAttributeSet com.android.cts.util/android.test.InstrumentationCtsTestRunner
#am instrument -w -r -e class android.util.cts.XmlTest com.android.cts.util/android.test.InstrumentationCtsTestRunner
#am instrument -w com.android.cts.util/android.test.InstrumentationCtsTestRunner

inst_params1 = {'class': 'android.util.cts.XmlTest',
               'method': 'testAsAttributeSet',
               'componment': 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'
               }

inst_params2 = {'class': 'android.util.cts.XmlTest',
               'method': 'testFindEncodingByName',
               'componment': 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'
               }

local_cmd = 'adb shell am instrument -w -r -e class %s#%s %s'

def instrument(method_name, class_name, componment_name):
    cmd = local_cmd % (class_name, method_name, componment_name)
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

class Caculator(unittest.TestCase):
    inst_class = 'android.util.cts.XmlTest'
    inst_componment = 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'

    def setUp(self):
        super(Caculator, self).setUp()
        #install apk
        #adb install [-r|-s] <apk file>

    def tearDown(self):
        super(Caculator, self).tearDown()
        #uninstall apk
        #adb [-k] uninstall <package name>

    def testCaculatorA(self):
        output = instrument('testAsAttributeSet', self.inst_class, self._componment)
        assert output['stream'].find('OK') != -1, ret

    def testCaculatorB(self):
        output = instrument('testFindEncodingByName', self.inst_class, self._componment)
        assert output['stream'].find('OK') != -1, ret
