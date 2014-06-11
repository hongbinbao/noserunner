#!/usr/bin/python
# -*- coding:utf-8 -*-\

import unittest
import planloader_test
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(planloader_test)
    unittest.TextTestRunner(verbosity=2).run(suite)