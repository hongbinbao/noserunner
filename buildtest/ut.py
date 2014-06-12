#!/usr/bin/python
# -*- coding:utf-8 -*-\

import os, re
import unittest
test_surfix = '\_test.py$'
if __name__ == '__main__':
    work_dir = os.path.abspath(os.path.dirname(__file__))
    gen = os.walk(work_dir)
    root_path, dirs, files  = gen.next()
    test = re.compile(test_surfix, re.IGNORECASE)
    files = filter(test.search, files)
    filename_to_module_name = lambda f: os.path.splitext(f)[0]
    module_names = map(filename_to_module_name, files)
    modules = map(__import__, module_names)
    load = unittest.defaultTestLoader.loadTestsFromModule
    suites = unittest.TestSuite(map(load, modules))
    unittest.TextTestRunner(verbosity=2).run(suites)