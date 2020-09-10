from RainyCore.item import Item
from RainyCore.monster import Monster
from RainyCore.spell import Spell
import os
import xml.etree.ElementTree as ElementTree
import json


class RainyDatabase:
    valid_spells = None
    valid_items = None
    valid_monsters = None

    def __init__(self, path, include_spells=True, include_items=True, include_monsters=True):
        self.entries = dict({
            str(Item):      dict(),
            str(Monster):   dict(),
            str(Spell):     dict()
        })
        self.path = path
        self.include_spells = include_spells
        self.include_items = include_items
        self.include_monsters = include_monsters
        self.create_srd_list(path)
        self.load_resources(path)

    def create_srd_list(self, path):
        path = os.path.join(path, "5", "srd_valid_DO_NOT_DELETE.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            srd_valid = json.loads(f.read())
        valid_spells = [i["name"] for i in srd_valid["spells"]["results"]]
        valid_monsters = [i["name"] for i in srd_valid["monsters"]["results"]]
        valid_items = [i["name"] for i in srd_valid["items"]["results"]]
        self.srd_dict = dict({
            str(Spell): valid_spells,
            str(Monster): valid_monsters,
            str(Item): valid_items
        })

    def load_resources(self, path):
        if self.include_items:
            self.load_items(path)
        if self.include_monsters:
            self.load_monsters(path)
        if self.include_spells:
            self.load_spells(path)
        self.load_collections(path)

        # self.item_table_widget.load_all("./item", "{}/{}/Items/".format(resource_path, self.version), item_cls)
        # self.item_table_widget.fill_table()
        # self.item_table_widget.define_filters(self.version)
        # self.monster_table_widget.load_all("./monster", "{}/{}/Bestiary/".format(resource_path, self.version), monster_cls)
        # self.monster_table_widget.fill_table()
        # self.monster_table_widget.define_filters(self.version)
        # self.spell_table_widget.load_all("./spell", "{}/{}/Spells/".format(resource_path, self.version), spell_cls)
        # self.spell_table_widget.fill_table()
        # self.spell_table_widget.define_filters(self.version)

    def load_items(self, path):
        self.load_all("./item", os.path.join(path, "5", "Items", ""), Item)

    def load_monsters(self, path):
        self.load_all("./monster", os.path.join(path, "5", "Bestiary", ""), Monster)

    def load_spells(self, path):
        self.load_all("./spell", os.path.join(path, "5", "Spells", ""), Spell)

    def load_collections(self, path):
        path = os.path.join(path, "5", "Collections")
        for resource in os.listdir(path):
            self.load_collection(path, resource)

    def load_collection(self, path, resource):
        xml = ElementTree.parse(os.path.join(path, resource))
        root = xml.getroot()
        # entry_dict = self.entries[str(Class)]
        if self.include_spells:
            for itt, entry in enumerate(root.findall("./spell")):
                self.insert_individual(Spell(entry, itt, self.srd_dict[str(Spell)]), self.entries[str(Spell)], resource)

        if self.include_monsters:
            for itt, entry in enumerate(root.findall("./monster")):
                self.insert_individual(Monster(entry, itt, self.srd_dict[str(Monster)]), self.entries[str(Monster)], resource)

        if self.include_items:
            for itt, entry in enumerate(root.findall("./item")):
                self.insert_individual(Item(entry, itt, self.srd_dict[str(Item)]), self.entries[str(Item)], resource)

    def load_all(self, s, dir, Class):
        for resource in os.listdir(dir):
            self.load_specific(s, dir, resource, Class)

    def load_specific(self, s, dir, resource, Class):
        xml = ElementTree.parse(dir + resource)
        root = xml.getroot()
        entry_dict = self.entries[str(Class)]
        for itt, entry in enumerate(root.findall(s)):
            entry_class = Class(entry, itt, self.srd_dict[str(Class)])
            self.insert_individual(entry_class, entry_dict, resource)

    def insert_individual(self, entry, dictionary, resource):
        # print("insert_individual", entry.name)
        if entry.name not in dictionary.keys():
            if type(entry) is Spell and "Invocation: " in entry.name:
                return
            dictionary[entry.name] = entry
        else:
            # print("\t", entry.name, "not in dictionary keys")
            if type(entry) is Spell:
                dictionary[entry.name].append_spell(entry)
            else:
                dictionary[entry.name].append_source(resource)

    def list(self, Class):
        entry_dict = self.entries[str(Class)]
        for name in entry_dict:
            print(name)

    def length(self, Class):
        return len(self.entries[str(Class)])

    def find(self, name, Class):
        entry_dict = self.entries[str(Class)]
        if name not in entry_dict.keys():
            return None
        else:
            return entry_dict[name]

    def validate(self, monster=True, spell=True, item=True):
        if spell:
            self.validate_individual(Spell)
        if monster:
            self.validate_monsters()
        if item:
            self.validate_item()

    def validate_monsters(self):
        print("Validating Monsters")
        self.validate_individual(Monster)  # validate database fields
        monsters = self.entries[str(Monster)]
        print("Trialing Actions:")
        for monster in monsters.values():
            if not hasattr(monster, "action_list"):
                continue
            for action in monster.action_list:
                if action is None:
                    print("\t! Faulty Action -", monster.name, action.name)
                elif not hasattr(action, "name"):
                    print("\t! Action without name -", monster.name)

    def validate_item(self):
        entries = self.entries[str(Item)]
        sources = []
        print("Validating Items")
        for name, entry in entries.items():
            skip_append = False
            if not hasattr(entry, "rarity"):
                print("\tNo Rarity:", entry.name)
            elif entry.rarity == "N/A":
                print("\tUnrealised entry:", entry.name)
            elif entry.rarity.lower() not in ["common", "uncommon", "rare", "very rare", "legendary", "artifact"]:
                print("\tFalse Rarity:", entry.name, entry.rarity)
            else:
                skip_append = True
            if not skip_append:
                for source in entry.source:
                    if source not in sources:
                        sources.append(source)
                continue
        print("Invalid items from following sources:", sources)

    def validate_individual(self, entry_class):
        entries = self.entries[str(entry_class)]
        for name, entry in entries.items():
            for req in entry.required_database_fields:
                if not hasattr(entry, req) or getattr(entry, req) is None:
                    print(req, ":", entry.name)

    def __getitem__(self, key):
        if key in [Item, Spell, Monster]:
            return self.entries[str(key)]
        else:
            return self.entries[key]


if __name__ == "__main__":
    db = RainyDatabase(os.getcwd())
    # db.list(Item)
    print(db.length(Item), db.length(Monster), db.length(Spell))
    db.validate(item=False, monster=True, spell=False)
