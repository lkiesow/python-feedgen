import unittest
from feedgen import util

class TestSequenceFunctions(unittest.TestCase):

    def test_listToHumanReadableStr(self):
        # Just check that none of the cases causes an error
        empty = util.listToHumanreadableStr([])
        one = util.listToHumanreadableStr([4])
        two = util.listToHumanreadableStr([4, "hi"])
        three = util.listToHumanreadableStr([4, "hi", "low"])

        assert "4" in one
        assert "and" not in one
        assert "," not in one

        assert "4" in two
        assert "and" in two
        assert "hi" in two
        assert "," not in two

        assert "4" in three
        assert "," in three
        assert "hi" in three
        assert "and" in three
        assert "low" in three
