from RainyDatabase import RainyDatabase, EntryType, System, Entry
import os
import unittest


class Test5EDatabase(unittest.TestCase):
    def setUp(self) -> None:
        if os.getcwd().endswith("tests"):
            path = ".."
        else:
            path = "."
        self.db = RainyDatabase(
            path=path,
            system=System.DnD5e,
            system_entry_classes=dict({
                EntryType.Monster: Entry,
                EntryType.Spell: Entry,
                EntryType.Item: Entry
            })
        )

    def test__load_system_classes(self):
        expected_classes = dict({
            EntryType.Monster: Entry,
            EntryType.Spell: Entry,
            EntryType.Item: Entry
        })
        self.assertDictEqual(expected_classes, self.db.entry_classes)

    def test_5e_monsters(self):
        self.db.validate(EntryType.Monster)

    def test_5e_spells(self):
        self.db.validate(EntryType.Spell)

    def test_get_monsters(self):
        monsters = self.db.get(EntryType.Monster)
        self.assertEqual(1723, len(monsters))

    def test_get_spells(self):
        spells = self.db.get(EntryType.Spell)
        self.assertEqual(508, len(spells))

    def test_get_items(self):
        items = self.db.get(EntryType.Item)
        self.assertEqual(1651, len(items))


