# -*- coding: utf-8

__author__="lreqc"
__date__ ="$2009-07-19 08:05:30$"

import unittest
import lqsoft.cstruct.test.test_numeric
import lqsoft.cstruct.test.test_strings
import lqsoft.cstruct.test.test_complex

test_cases = [
    lqsoft.cstruct.test.test_complex,
    lqsoft.cstruct.test.test_numeric,
    lqsoft.cstruct.test.test_strings,
]

if __name__ == "__main__":
    loader = unittest.TestLoader()

    for name in test_cases:
        suite = loader.loadTestsFromModule(name)
        unittest.TextTestRunner(verbosity=3).run(suite)
