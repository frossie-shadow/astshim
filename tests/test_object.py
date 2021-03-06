from __future__ import absolute_import, division, print_function
import unittest

import numpy as np

import astshim
from astshim.test import ObjectTestCase


class TestObject(ObjectTestCase):

    def test_attributes(self):
        """Test accessing object attributes
        """
        nin = 2
        zoom = 1.3
        obj = astshim.ZoomMap(nin, zoom)

        self.assertEqual(obj.className, "ZoomMap")

        self.assertTrue(obj.hasAttribute("ID"))
        self.assertTrue(obj.hasAttribute("Ident"))
        self.assertTrue(obj.hasAttribute("UseDefs"))

        self.assertEqual(obj.id, "")
        self.assertEqual(obj.ident, "")
        self.assertEqual(obj.useDefs, True)

    def test_clear_and_test(self):
        """Test Object.clear and Object.test"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertFalse(obj.test("ID"))
        obj.id = "initial_id"
        self.assertEqual(obj.id, "initial_id")
        self.assertTrue(obj.test("ID"))
        obj.clear("ID")
        self.assertEqual(obj.id, "")
        self.assertFalse(obj.test("ID"))

    def test_copy_and_same(self):
        """Test Object.copy and Object.same"""
        obj = astshim.ZoomMap(2, 1.3, "Ident=original")

        # there may be more than one object in existence if run with pytest
        initialNumObj = obj.getNObject()

        self.checkCopy(obj)
        cp = obj.copy()
        # a deep copy does not increment
        self.assertEqual(obj.getRefCount(), 1)

        seriesMap = obj.then(obj)
        # obj itself plus two copies in the SeriesMap
        self.assertEqual(obj.getRefCount(), 3)
        del seriesMap
        self.assertEqual(obj.getRefCount(), 1)

        cp.ident = "copy"
        self.assertEqual(cp.ident, "copy")
        self.assertEqual(obj.ident, "original")

        del cp
        self.assertEqual(obj.getNObject(), initialNumObj)
        self.assertEqual(obj.getRefCount(), 1)

    def test_error_handling(self):
        """Test handling of AST errors
        """
        # To introduce an AST error construct a PolyMap with no inverse mapping
        # and then try to transform in the inverse direction.
        coeff_f = np.array([
            [1.2, 1, 2, 0],
            [-0.5, 1, 1, 1],
            [1.0, 2, 0, 1],
        ])
        pm = astshim.PolyMap(coeff_f, 2, "IterInverse=0")
        indata = np.array([
            [1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0],
        ])

        # make sure the error string contains "Error"
        try:
            pm.applyInverse(indata)
        except RuntimeError as e:
            self.assertEqual(e.args[0].count("Error"), 1)
            print(e)

        # cause another error and make sure the first error message was purged
        try:
            pm.applyInverse(indata)
        except RuntimeError as e:
            self.assertEqual(e.args[0].count("Error"), 1)

    def test_equality(self):
        """Test __eq__ and __ne__
        """
        frame = astshim.Frame(2)
        zoomMap = astshim.ZoomMap(2, 1.5)
        frameSet1 = astshim.FrameSet(frame, zoomMap, frame)
        frameSet2 = astshim.FrameSet(frame, zoomMap, frame)
        self.assertTrue(frameSet1 == frameSet2)
        self.assertFalse(frameSet1 != frameSet2)
        self.assertEqual(frameSet1, frameSet2)

        # the base attribute of frameSet1 is not set; set the base attribute
        # of framesSet2 and make sure the frame sets are now not equal
        self.assertFalse(frameSet1.test("Base"))
        frameSet2.base = 1
        self.assertTrue(frameSet2.test("Base"))
        self.assertFalse(frameSet1 == frameSet2)
        self.assertTrue(frameSet1 != frameSet2)
        self.assertNotEqual(frameSet1, frameSet2)

        # make sure base is unset in the inverse of the inverse of frameSet1,
        # else the equality test will fail for hard-to-understand reasons
        self.assertFalse(frameSet1.getInverse().getInverse().test("Base"))
        self.assertNotEqual(frameSet1, frameSet1.getInverse())
        self.assertEqual(frameSet1, frameSet1.getInverse().getInverse())
        self.assertFalse(frameSet1.getInverse().getInverse().test("Base"))

        frame3 = astshim.Frame(2)
        frame3.title = "Frame 3"
        frameSet3 = astshim.FrameSet(frame3)
        self.assertNotEqual(frameSet1, frameSet3)

    def test_id(self):
        """Test that ID is *not* transferred to copies"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertEqual(obj.id, "")
        obj.id = "initial_id"
        self.assertEqual(obj.id, "initial_id")
        cp = obj.copy()
        self.assertEqual(cp.id, "")

    def test_ident(self):
        """Test that Ident *is* transferred to copies"""
        obj = astshim.ZoomMap(2, 1.3)

        self.assertEqual(obj.ident, "")
        obj.ident = "initial_ident"
        self.assertEqual(obj.ident, "initial_ident")
        cp = obj.copy()
        self.assertEqual(cp.ident, "initial_ident")

    def test_show(self):
        obj = astshim.ZoomMap(2, 1.3)
        desShowLines = [
            " Begin ZoomMap \t# Zoom about the origin",
            "    Nin = 2 \t# Number of input coordinates",
            " IsA Mapping \t# Mapping between coordinate systems",
            "    Zoom = 1.3 \t# Zoom factor",
            " End ZoomMap",
            "",
        ]
        desShowLinesNoComments = [
            " Begin ZoomMap",
            "    Nin = 2",
            " IsA Mapping",
            "    Zoom = 1.3",
            " End ZoomMap",
            "",
        ]
        self.assertEqual(obj.show(), "\n".join(desShowLines))
        self.assertEqual(obj.show(True), "\n".join(desShowLines))
        self.assertEqual(obj.show(False), "\n".join(desShowLinesNoComments))


if __name__ == "__main__":
    unittest.main()
