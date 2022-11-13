from RainyDatabase import RainyDatabase, EntryType
from RainyCore import System, MonsterSW5e, PowerSW5e, ItemSW5e
import os
import unittest


class TestSW5EDatabase(unittest.TestCase):
    def setUp(self) -> None:
        if os.getcwd().endswith("tests"):
            path = ".."
        else:
            path = "."
        self.db = RainyDatabase(path=path, system=System.SW5e)

    def test__load_system_classes(self):
        expected_classes = dict({
            EntryType.Monster: MonsterSW5e,
            EntryType.Spell: PowerSW5e,
            EntryType.Item: ItemSW5e
        })
        self.assertDictEqual(expected_classes, self.db.entry_classes)

    def test_sw5e_monsters(self):
        self.db.validate_monsters()

    def test_sw5e_spells(self):
        self.db.validate_spells()

    def test_get_monsters(self):
        monsters = self.db.get_monsters()
        self.assertEqual(113, len(monsters))

    def test_get_spells(self):
        spells = self.db.get_spells()
        self.assertEqual(310, len(spells))

    def test_get_items(self):
        items = self.db.get_items()
        self.assertEqual(0, len(items))
