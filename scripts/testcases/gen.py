#!/usr/bin/python
# -*- coding:utf-8 -*-
from commands import getoutput as call
import sys, time

inst_params = {'class': 'android.util.cts.XmlTest',
               'method': 'testAsAttributeSet',
               'componment': 'com.android.cts.util/android.test.InstrumentationCtsTestRunner'


#local_cmd_tmp = 'adb shell am instrument -e class <class_name>#<method> -w <TEST_PACKAGE_NAME>/<RUNNER_CLASS_NAME>

local_cmd = 'adb shell am instrument -w -r -e class %s#%s %s'

def instrument(params):
    cmd = local_cmd % (params['class'], params['method'], params['componment'])
    ret = call(cmd)
    if ret.find('OK') == -1:
        assert 1, 'ok'
    else:
        assert 0, 'inst failed'


def testGen():
    yield instrument, inst_params

inst_params2 = {'class': 'android.util.cts.XmlTest',
               'method': 'testAsAttributeSet',
               'package': 'com.android.cts.util',
               'runner': 'android.test.InstrumentationCtsTestRunner'}

#adb shell am instrument -e class android.util.cts.XmlTest#testAsAttributeSet -w com.android.cts.util/android.test.InstrumentationCtsTestRunner

#tmp adb shell am instrument -e class <class_name>#<method> -w <TEST_PACKAGE_NAME>/<RUNNER_CLASS_NAME>
#1:a full-qualified Java class name for one of the test case class. only the test case class is executed
#2:a ful-qualified Java class name and one of its method. only the method is executed.
#note the hash mark(#) between the class name and the method name.

#{'class': 'android.util.cts.XmlTest'}
#monkeyrrunner
#1>>>  d.instrument('com.android.cts.util/android.test.InstrumentationCtsTestRunner', {'class': 'android.util.cts.XmlTest'})
#2>>>  d.instrument('com.android.cts.util/android.test.InstrumentationCtsTestRunner', {'class': 'android.util.cts.XmlTest#testAsAttributeSet'})
#instrument [options] <COMPONENT> Start monitoring with an Instrumentation instance.
#Typically the target <COMPONENT> is the form <TEST_PACKAGE>/<RUNNER_CLASS>.
#Options are:

#-r: Print raw results (otherwise decode <REPORT_KEY_STREAMRESULT>). Use with [-e perf true] to generate raw output for performance measurements.
#-e <NAME> <VALUE>: Set argument <NAME> to <VALUE>. For test runners a common form is -e <testrunner_flag> <value>[,<value>...].
#-p <FILE>: Write profiling data to <FILE>.
#-w: Wait for instrumentation to finish before returning. Required for test runners.
#--no-window-animation: Turn off window animations while running.
#--user <USER_ID> | current: Specify which user instrumentation runs in; curren

