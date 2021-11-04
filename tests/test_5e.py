from RainyDatabase import RainyDatabase, EntryType
from RainyCore import System, Monster, Spell, Item
import os
import unittest


class Test5EDatabase(unittest.TestCase):
    def setUp(self) -> None:
        if os.getcwd().endswith("tests"):
            path = ".."
        else:
            path = "."
        self.db = RainyDatabase(path=path, system=System.DnD5e)

    def test__load_system_classes(self):
        expected_classes = dict({
            EntryType.Monster: Monster,
            EntryType.Spell: Spell,
            EntryType.Item: Item
        })
        self.assertDictEqual(expected_classes, self.db.entry_classes)

    def test_sw5e_monsters(self):
        self.db.validate_monsters()

    def test_sw5e_spells(self):
        self.db.validate_spells()

    def test_get_monsters(self):
        monsters = self.db.get_monsters()
        self.assertEqual(1723, len(monsters))

    def test_get_spells(self):
        spells = self.db.get_spells()
        self.assertEqual(508, len(spells))

    def test_get_items(self):
        items = self.db.get_items()
        self.assertEqual(1651, len(items))


