# tests/test_Unit.py

import unittest
from datetime import datetime

from Model.Unit import Unit


class TestUnitCreateFromDict(unittest.TestCase):

    def test_create_from_dict_success(self):
        data = {
            'name': 'Sample Unit',
            'sequence': 1,
            'opening_date': datetime(2025, 1, 1),
            'closing_date': datetime(2025, 1, 15),
            'end_date': datetime(2025, 1, 31),
            'description': 'A description of the unit'
        }
        unit = Unit.create_from_dict(data)

        self.assertEqual('Sample Unit', unit._name)
        self.assertEqual(1, unit.sequence)
        self.assertEqual(datetime(2025, 1, 1), unit.opening_date)
        self.assertEqual(datetime(2025, 1, 15), unit.closing_date)
        self.assertEqual(datetime(2025, 1, 31), unit.end_date)
        self.assertEqual('A description of the unit', unit.description)

    def test_create_from_dict_empty_dict(self):
        with self.assertRaises(ValueError) as context:
            Unit.create_from_dict({})
        self.assertEqual(str(context.exception), "Empty dictionary passed to create_from_dict")

    def test_create_from_dict_missing_fields(self):
        data = {
            'name': 'Unit Without Dates',
            'sequence': 2
        }
        unit = Unit.create_from_dict(data)

        self.assertEqual('Unit Without Dates', unit._name)
        self.assertEqual(2, unit.sequence)
        self.assertEqual('', unit.description)
        self.assertIsInstance(unit.opening_date, datetime)
        self.assertIsInstance(unit.closing_date, datetime)
        self.assertIsInstance(unit.end_date, datetime)


if __name__ == "__main__":
    unittest.main()
