import unittest

import hello
from hello import cmake_generated_module


class HelloTest(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello.who(), "world")

        with open("test_hello.completed.txt", "w") as marker:
            marker.write("")

    def test_cmake_generated_module(self):
        self.assertEqual(cmake_generated_module.what(), "cmake_generated_module")


if __name__ == "__main__":
    unittest.main()
