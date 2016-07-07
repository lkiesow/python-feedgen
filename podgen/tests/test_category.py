# -*- coding: utf-8 -*-
"""
    podgen.tests.test_category
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module for testing the Category class.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
import unittest

from podgen import Category


class TestCategory(unittest.TestCase):
    def test_constructorWithSubcategory(self):
        c = Category("Arts", "Food")
        self.assertEqual(c.category, "Arts")
        self.assertEqual(c.subcategory, "Food")

    def test_constructorWithoutSubcategory(self):
        c = Category("Arts")
        self.assertEqual(c.category, "Arts")
        self.assertTrue(c.subcategory is None)

    def test_constructorInvalidCategory(self):
        self.assertRaises(ValueError, Category, "Farts", "Food")

    def test_constructorInvalidSubcategory(self):
        self.assertRaises(ValueError, Category, "Arts", "Flood")

    def test_constructorSubcategoryWithoutCategory(self):
        self.assertRaises((ValueError, TypeError), Category, None, "Food")

    def test_constructorCaseInsensitive(self):
        c = Category("arTS", "FOOD")
        self.assertEqual(c.category, "Arts")
        self.assertEqual(c.subcategory, "Food")

    def test_immutable(self):
        c = Category("Arts", "Food")
        self.assertRaises(AttributeError, setattr, c, "category", "Technology")
        self.assertEqual(c.category, "Arts")

        self.assertRaises(AttributeError, setattr, c, "subcategory", "Design")
        self.assertEqual(c.subcategory, "Food")

    def test_escapedIsAccepted(self):
        c = Category("Sports &amp; Recreation", "College &amp; High School")
        self.assertEqual(c.category, "Sports & Recreation")
        self.assertEqual(c.subcategory, "College & High School")
