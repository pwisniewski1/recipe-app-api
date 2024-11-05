"""
Sample tests
"""

from django.test import SimpleTestCase
from app.calc import add, subtract


class CalcTests(SimpleTestCase):
    """_summary_

    Args:
        SimpleTestCase (_type_): _description_
    """

    def test_add_numbers(self):
        """Test adding numbers together"""
        res = add(5, 6)
        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        res = subtract(3, 6)
        self.assertEqual(res, -3)
