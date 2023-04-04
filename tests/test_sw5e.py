from RainyDatabase import RainyDatabase, EntryType, Entry, System
import os
import unittest


class TestSW5EDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = RainyDatabase(
            system=System.SW5e,
            system_entry_classes={
                EntryType.Monster: Entry,
                EntryType.Power: Entry,
                EntryType.Item: Entry
            }
        )

    def test_get_monsters(self):
        monsters = self.db.get(EntryType.Monster)
        self.assertEqual(271, len(monsters))

    def test_get_spells(self):
        spells = self.db.get(EntryType.Power)
        self.assertEqual(465, len(spells))

    def test_get_items(self):
        items = self.db.get(EntryType.Item)
        self.assertEqual(507, len(items))
