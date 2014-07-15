#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import nose
from planloader import PlanLoaderPlugin
from reporter import ReporterPlugin
from xmlreportplugin import XmlReporterPlugin

'''
launcher of testing.
'''

def showUsage():
    print 'usage:'
    print '\tpython runtests.py [-h|--help] [--cycle CYCLE] [--duration DURATION_TIME] [--timeout TIMEOUT_VALUE_SECONDS] [--livereport] [--server-config REPORT_CONFIG] [--client-config DEVICE_CONFIG] [,[argv]]\n\n'
    print 'Process the paramters of runtests'
    print 'optional arguments:'
    print '\t-h, --help            Show this help message and exit\n'
    print '\t--cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle. Default is 1\n'
    print '\t--plan-file PLAN      Set the absolute path or relative path of test plan file. If not provide this option. The "plan" file in current directory will be used as default\n'
    print '\t--duration DURATION   The minumum test duration before ending the test\n'
    print                          '\t\t\t\t\tHere format must follow next format: xxDxxHxxMxxS\n'
    print                          '\t\t\t\t\te.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds\n'
    print '\t--timeout SECONDS     The timeout specified in seconds to limit the maximum period of test case method execution. Default is 180 seconds\n'
    print '\t--livereport          Enable the report server feature. Default is disable\n'
    print '\t--server-config       Specify the path of live report server configuration file. If not provide this option. The "server.config" file in current directory will be used as default\n'
    print '\t--client-config       Specify the path of device configuration file. If not provide this option. The "client.config" file in current directory will be used as default\n'
    print '\t--verbosity           Set the level(1~5) of verbosity to get the help string of every test and the result. Default is 2\n'
    print '\targv                  Additional arguments accepted by nose\n'
    exit(1)

DEFAULT_VERBOSITY = '2'
if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv: showUsage()
    cycle = None
    arg_copy = sys.argv[:]
    if len(arg_copy) >= 2:
        if '--duration' not in arg_copy and '--cycle' not in arg_copy:
            print '\nmiss --duration or --cycle!\n'
            showUsage()
        prog_name = arg_copy.pop(0)
        arg_copy.insert(0, '')
        arg_copy.insert(1, '--with-plan-loader')
        arg_copy.insert(2, '--with-live-reporter')
        if '--cycle' in arg_copy:
            index = arg_copy.index('--cycle')
            cycle = int(arg_copy[index+1])
            arg_copy[index] = '--icycle'
        if '--verbosity' not in arg_copy:
            arg_copy.append('--verbosity')
            arg_copy.append(DEFAULT_VERBOSITY)
    else:
        showUsage()
    try:
        planloader = PlanLoaderPlugin()
        reporter = ReporterPlugin()
        xmlreportplugin = XmlReporterPlugin()
        if not cycle:
            while True:
                nose.run(argv=arg_copy, addplugins=[planloader, reporter, xmlreportplugin])
        else:
            for i in range(cycle):
                nose.run(argv=arg_copy, addplugins=[planloader, reporter, xmlreportplugin])
    except KeyboardInterrupt:
        pass
