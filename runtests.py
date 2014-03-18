#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import nose
from planloader import PlanLoaderPlugin
from reporter import ReporterPlugin

'''
launcher of testing
'''

def showUsage():
    print 'usage:'
    print '\tpython runtests.py [-h|--help] [--cycle CYCLE] [--reportserver]\n\n'
    print 'Process the paramters of runtests'

    print 'optional arguments:'
    print '\t-h, --help            Show this help message and exit\n'
    print '\t--cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle. Default is 1\n'
    print '\t--plan PLAN           Set the absolute path or relative path of test plan file.Default is current directory\n'
    print '\t--duration DURATION   The minumum test duration before ending the test\n'
    print                          '\t\t\t\t\tHere format must follow next format: xxDxxHxxMxxS\n'
    print                          '\t\t\t\t\te.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds\n'
    print '\t--reportserver        Enable the report server feature. Default is disable\n'
    print '\t--verbosity           Set the level(1~5) of verbosity to get the help string of every test and the result. Default is 2\n'
    exit(1)

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv: showUsage()
    cycle = None
    argvs = ['','--with-plan-loader', '--with-reporter']
    if '--duration' not in sys.argv and '--cycle' not in sys.argv:
        print '\nmiss --duration or --cycle!\n'
        showUsage()
    if len(sys.argv) >= 2:
        if '--verbosity' not in sys.argv:
            argvs.append('--verbosity')
            argvs.append('2')
        else:
            index = sys.argv.index('--verbosity')
            verbosity = sys.argv[int(index)+1]
            argvs.append('--verbosity')
            argvs.append(verbosity)

        if '--cycle' in sys.argv:
            index = sys.argv.index('--cycle')
            cycle = int(sys.argv[int(index)+1])
            argvs.append('--cycle')
            argvs.append(str(cycle))            

        if '--plan' in sys.argv:
            index = sys.argv.index('--plan')
            plan = sys.argv[int(index)+1]
            argvs.append('--plan')         
            argvs.append(plan)

        if '--reportserver' in sys.argv:
            argvs.append('--reportserver')

        if '--duration' in sys.argv:
            index = sys.argv.index('--duration')
            duration = sys.argv[int(index)+1]
            argvs.append('--duration')
            argvs.append(duration)

    planloader = PlanLoaderPlugin()
    reporter = ReporterPlugin()
    if not cycle:
        while True:
            nose.run(argv=argvs, addplugins=[planloader, reporter])
    else:
        for i in range(cycle):
            nose.run(argv=argvs, addplugins=[planloader, reporter])
