#!/usr/bin/env python3

import unittest

from prk import IdFactory


class TestIdFactory(unittest.TestCase):

    def test_iter_footprint(self):
        string = "001234567890ABCDEF"
        factory = IdFactory()

        for extract in factory._iter_footprint(string):
            print(extract)

        self.assertTrue("Güt!")



if __name__ == "__main__":
    unittest.main()
