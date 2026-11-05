import unittest

from scripts.conversions import clean_price, parse_date

class TestConversions(unittest.TestCase):

    def test_clean_price(self):
        self.assertEqual(clean_price("€343,000.00"), 343000)
        self.assertEqual(clean_price("€110,132.15"), 110132)
        self.assertEqual(clean_price("€285,000.50"), 285001)

    def test_invalid_price(self):
        self.assertIsNone(clean_price(""))
        self.assertIsNone(clean_price("invalid"))
        self.assertIsNone(clean_price(None))
        self.assertIsNone(clean_price("-100"))

    def test_parse_date(self):
        self.assertEqual(parse_date("01/01/2010"), "2010-01-01")
        self.assertEqual(parse_date("23/10/2026"), "2026-10-23")

    def test_invalid_date(self):
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date("31/02/2026"))
        self.assertIsNone(parse_date(None))


if __name__ == "__main__":
    unittest.main()
