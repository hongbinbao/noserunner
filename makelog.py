#!/usr/bin/python
# -*- coding:utf-8 -*- 
import os, time, sys

'''
script to make an entire log from report(fail|pass|error) folder.
'''

DEFAULT_ALL_LOG_NAME = 'alllog.txt'
def show_usage():
    print 'usage:'
    print '\tpython makelog.py [-h|--help] <-d REPORT_DIRECTORY_PATH> [-f ENTIRE_LOG_FILE_NAME]\n\n'
    print 'Process the paramters of makelog'

    print 'optional arguments:'
    print '\t-h, --help                    Show this help message and exit\n'
    print '\t-d REPORT_DIRECTORY_PATH      Set the directory path of report\n'
    print '\t-f ENTIRE_LOG_FILE_NAME       Set the file name of entire log with the related or absolute path\n'
    exit(1)

def callback(fs):
    name = os.path.basename(fs)
    p,f = name.split('@')
    return int(time.mktime(time.strptime(f, '%Y-%m-%d_%H:%M:%S')))

def gen_all(wd):
    gen = os.walk(wd)
    root_path, target_dir, _  = gen.next()
    for td in target_dir:
        inner_path, case_dir , __ = os.walk(os.path.join(root_path,td)).next()
        for cd in case_dir:
            yield os.path.abspath(os.path.join(inner_path, cd))

def make_log(dirs, fname):
    log_path = None
    if os.path.isabs(fname):
        log_path = fname
    else:
        log_path = os.path.join(os.getcwd(), fname)
    if os.path.exists(log_path): raise Exception('%s already exists' % log_path)
    a =  sorted(gen_all(dirs), key=callback)
    with open(log_path, 'wa+') as l:
        for f in a:
            lf = os.path.join(os.path.join(f, 'logs'),'log.txt')
            content = None
            with open(lf, 'r') as ff:
                content = ff.read()
                l.write(content)
    print '\n%s saved success.' % log_path

if __name__ == '__main__':
    report_dir = None
    entire_log_name = DEFAULT_ALL_LOG_NAME
    if '-h' in sys.argv or '--help' in sys.argv:
        show_usage()
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        entire_log_name = sys.argv[int(index)+1]
    if '-d' not in sys.argv:
        show_usage()
    if '-d' in sys.argv:
        index = sys.argv.index('-d')
        report_dir = os.path.abspath(sys.argv[int(index)+1])
        if not os.path.exists(report_dir) and not os.path.isdir(report_dir):
            show_usage()
    make_log(report_dir, entire_log_name)
