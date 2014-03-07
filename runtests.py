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
    print '\t--reportserver        Enable the report server feature. Default is disable\n'
    exit(1)

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv: showUsage()
    cycle = 1
    argvs = ['','--with-plan-loader', '--verbosity=2', '--with-reporter', '--cycle=1']
    if len(sys.argv) >= 2:
        if '--cycle' in sys.argv:
            index = sys.argv.index('--cycle')
            cycle = int(sys.argv[int(index)+1])
        if '--reportserver' in sys.argv:
            argvs.append('--reportserver')
    planloader = PlanLoaderPlugin()
    reporter = ReporterPlugin()
    for i in range(cycle):
        nose.run(argv=argvs, addplugins=[planloader, reporter])
        #nose.main(addplugins=[PlanLoaderPlugin(), DeviceConfigPlugin(), FileOutputPlugin()])
        #nose.run(argv=['','--with-plan-loader', '--verbosity=5','--with-device-config','--with-file-output'])
