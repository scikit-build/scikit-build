#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_test123
----------------------------------

Test to verify the test1 packages for PyCMake's test1
"""

import unittest

class TestTest1(unittest.TestCase):

    def setUp(self):
        pass

    def test_import(self):
        """Verify import of libtest1."""
        import test1

    def test_test123(self):
        """Verify "test123" the method from the CPython extension."""
        from test1 import test123
        self.assertEqual(test123(), 123)
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
