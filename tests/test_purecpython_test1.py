#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_PureCPython
----------------------------------

Test to build and test a Pure CPython module with PyCMake.
"""
from __future__ import print_function

import unittest

import os
import sys
import subprocess



CMAKE_COMMAND="cmake"
SOURCE_DIR=os.path.abspath("tests/test1") # assume in root of PyCMake
BINARY_DIR=os.path.abspath("tests/test1/build")

class TestPureCPython(unittest.TestCase):

    def setUp(self):
        pass

    def test_configure(self):
        """ TODO: Implement me! """
        if not os.path.exists(BINARY_DIR):
            os.mkdir(BINARY_DIR)
        else:
            # the old build should be automatically remove...
            print("Error: please remove binary dir \"{0}\"".format(BINARY_DIR))
            error

        cmake_cmd = [CMAKE_COMMAND ]
        #cmake_cmd += ['-DPYTHON_EXECUTABLE:PATH=' + sys.executable, ]
        cmake_cmd += [ SOURCE_DIR ]
        #cmake_cmd = ' '.join(cmake_cmd)
        print(cmake_cmd)
        rtn = subprocess.check_call(cmake_cmd, cwd=BINARY_DIR)

        self.assertEqual(rtn, 0) # configure result

    def test_build(self):
        """ TODO: Implement me! """

        # Run: cmake_command --build BINARY_DIR
        cmake_cmd = [CMAKE_COMMAND, "--build", BINARY_DIR]
        #cmake_cmd = ' '.join(cmake_cmd)
        print(cmake_cmd)
        rtn = subprocess.check_call(cmake_cmd, cwd=BINARY_DIR)
        self.assertEqual(rtn, 0) # buid result

    def test_install(self):
        """ TODO: Implement me! """

        # PYTHON SOURCE_DIR/setup.py install

        pass

    def test_test(sefl):
        """ TODO: Implement me! """

        # PYTHON SOURCE_DIR/setup.py test
        pass


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
