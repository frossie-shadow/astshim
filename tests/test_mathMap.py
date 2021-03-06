from __future__ import absolute_import, division, print_function
import unittest

import numpy as np
from numpy.testing import assert_allclose

import astshim
from astshim.test import MappingTestCase


class TestMathMap(MappingTestCase):

    def test_MathMapInvertible(self):
        mathmap = astshim.MathMap(2, 2,
                                  ["r = sqrt(x * x + y * y)",
                                   "theta = atan2(y, x)"],
                                  ["x = r * cos(theta)", "y = r * sin(theta)"],
                                  "SimpIF=1, SimpFI=1, Seed=-57")
        self.assertEqual(mathmap.className, "MathMap")
        self.assertEqual(mathmap.nIn, 2)
        self.assertEqual(mathmap.nOut, 2)

        self.checkBasicSimplify(mathmap)
        self.checkCopy(mathmap)
        self.checkPersistence(mathmap)

        indata = np.array([
            [1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0],
        ])
        outdata = mathmap.applyForward(indata)
        x = indata[0]
        y = indata[1]
        r = outdata[0]
        theta = outdata[1]
        pred_r = np.sqrt(x * x + y * y)
        pred_theta = np.arctan2(y, x)
        assert_allclose(r, pred_r)
        assert_allclose(theta, pred_theta)

        self.checkRoundTrip(mathmap, indata)

        self.assertEqual(mathmap.seed, -57)
        self.assertTrue(mathmap.simpFI)
        self.assertTrue(mathmap.simpIF)

    def test_MathMapNonInvertible(self):
        mathmap = astshim.MathMap(2, 1,
                                  ["r = sqrt(x * x + y * y)"],
                                  ["x = r", "y = 0"])
        self.assertEqual(mathmap.className, "MathMap")
        self.assertEqual(mathmap.nIn, 2)
        self.assertEqual(mathmap.nOut, 1)

        self.checkPersistence(mathmap)
        with self.assertRaises(AssertionError):
            self.checkBasicSimplify(mathmap)

        self.assertFalse(mathmap.simpFI)
        self.assertFalse(mathmap.simpIF)


if __name__ == "__main__":
    unittest.main()
