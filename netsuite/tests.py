#!/usr/bin/env python3
import unittest


class NetsuiteTestCase(unittest.TestCase):

    def test_dummy(self):
        x = '1'
        self.assertEqual(x, '1')
        self.assertTrue(x.endswith('1'))


if __name__ == "__main__":
     unittest.main()
