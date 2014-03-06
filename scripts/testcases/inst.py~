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

inst_params = {'class': 'android.util.cts.XmlTest',
               'method': 'testAsAttributeSet',
               'componment': 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'
               }
local_cmd = 'adb shell am instrument -w -r -e class %s#%s %s'

def instrument(params):
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

class Caculator(unittest.TestCase):
    def setUp(self):
        super(Caculator, self).setUp()
        #install apk
        #adb install [-r|-s] <apk file>

    def tearDown(self):
        super(Caculator, self).tearDown()
        #uninstall apk
        #adb [-k] uninstall <package name>

    def testCaculator(self):
        #yield instrument, inst_params
        output = instrument(inst_params)
        assert output['stream'].find('OK') != -1, ret

#instrument [options] <COMPONENT> Start monitoring with an Instrumentation instance.
#Typically the target <COMPONENT> is the form <TEST_PACKAGE>/<RUNNER_CLASS>.
#Options are:

#-r: Print raw results (otherwise decode <REPORT_KEY_STREAMRESULT>). Use with [-e perf true] to generate raw output for performance measurements.
#-e <NAME> <VALUE>: Set argument <NAME> to <VALUE>. For test runners a common form is -e <testrunner_flag> <value>[,<value>...].
#-p <FILE>: Write profiling data to <FILE>.
#-w: Wait for instrumentation to finish before returning. Required for test runners.
#--no-window-animation: Turn off window animations while running.
#--user <USER_ID> | current: Specify which user instrumentation runs in; current user if not specified.
