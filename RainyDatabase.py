from enum import Enum
import os
import xml.etree.ElementTree as ElementTree
import json


class EntryType(Enum):
    Monster = "monster"
    Spell = "spell"
    Item = "item"


class RainyDatabase:
    valid_spells = None
    valid_items = None
    valid_monsters = None

    def __init__(self, path, system, include_spells=True, include_items=True, include_monsters=True):
        self.system = system
        monster_cls, item_cls, spell_cls = self.system.get_system_classes()
        self.entry_classes = dict({
            EntryType.Monster: monster_cls,
            EntryType.Spell: spell_cls,
            EntryType.Item: item_cls
        })
        self.entries = dict({
            EntryType.Monster: dict(),
            EntryType.Spell: dict(),
            EntryType.Item: dict()
        })
        self.path = path
        self.include_spells = include_spells
        self.include_items = include_items
        self.include_monsters = include_monsters
        self.create_srd_list(path)
        self.load_resources(path, system=system)

    def create_srd_list(self, path):
        if self.system.is_DnD5e():
            path = os.path.join(path, "5", "srd_valid_DO_NOT_DELETE.json")
            if not os.path.exists(path):
                self.srd_dict = None
                return
            with open(path, "r") as f:
                srd_valid = json.loads(f.read())
            valid_spells = [i["name"] for i in srd_valid["spells"]["results"]]
            valid_monsters = [i["name"] for i in srd_valid["monsters"]["results"]]
            valid_items = [i["name"] for i in srd_valid["items"]["results"]]
            self.srd_dict = dict({
                EntryType.Spell: valid_spells,
                EntryType.Monster: valid_monsters,
                EntryType.Item: valid_items
            })
        else:
            self.srd_dict = None

    def get_monsters(self):
        return self.entries[EntryType.Monster]

    def get_spells(self):
        return self.entries[EntryType.Spell]

    def get_items(self):
        return self.entries[EntryType.Item]

    def load_resources(self, path, system):
        if self.include_items:
            self.load_items(path, system=system)
        if self.include_monsters:
            self.load_monsters(path, system=system)
        if self.include_spells:
            self.load_spells(path, system=system)

        if self.system.is_DnD5e():
            self.load_collections(path)

    def load_items(self, path, system):
        if self.system.is_DnD5e():
            path = os.path.join(path, "5", "Items", "")
        elif self.system.is_SW5e():
            path = os.path.join(os.path.join(path, "sw5e", "Items", ""))
        self.load_all("./item", path, EntryType.Item)

    def load_monsters(self, path, system):
        if self.system.is_DnD5e():
            path = os.path.join(os.path.join(path, "5", "Bestiary", ""))
        elif self.system.is_SW5e():
            path = os.path.join(os.path.join(path, "sw5e", "Monsters", ""))
        self.load_all("./monster", path, EntryType.Monster)

    def load_spells(self, path, system):
        if self.system.is_DnD5e():
            path = os.path.join(path, "5", "Spells", "")
        elif self.system.is_SW5e():
            path = os.path.join(path, "sw5e", "Spells", "")
        self.load_all("./spell", path, EntryType.Spell)

    def load_collections(self, path):
        path = os.path.join(path, "5", "Collections")
        for resource in os.listdir(path):
            self.load_collection(path, resource)

    def load_collection(self, path, resource):
        xml = ElementTree.parse(os.path.join(path, resource))
        root = xml.getroot()
        if self.include_spells:
            for itt, entry in enumerate(root.findall("./spell")):
                self.insert_individual(
                    self.entry_classes[EntryType.Spell](entry, itt, self.srd_dict),
                    self.get_spells(),
                    resource,
                    EntryType.Spell
                )

        if self.include_monsters:
            for itt, entry in enumerate(root.findall("./monster")):
                self.insert_individual(
                    self.entry_classes[EntryType.Monster](entry, itt, self.srd_dict),
                    self.get_monsters(),
                    resource,
                    EntryType.Monster
                )

        if self.include_items:
            for itt, entry in enumerate(root.findall("./item")):
                self.insert_individual(
                    self.entry_classes[EntryType.Item](entry, itt, self.srd_dict),
                    self.get_items(),
                    resource,
                    EntryType.Item
                )

    def load_all(self, s, dir, entry_type):
        for resource in os.listdir(dir):
            self.load_specific(s, dir, resource, entry_type)

    def load_specific(self, s, dir, resource, entry_type):
        xml = ElementTree.parse(dir + resource)
        root = xml.getroot()
        entry_dict = self.entries[entry_type]
        entry_class = self.entry_classes[entry_type]
        for itt, entry in enumerate(root.findall(s)):
            entry_instance = entry_class(entry, itt, self.srd_dict)
            self.insert_individual(entry_instance, entry_dict, resource, entry_type)

    def insert_individual(self, entry, dictionary, resource, entry_type):
        if entry.name not in dictionary.keys():
            if entry_type == EntryType.Spell and "Invocation: " in entry.name:
                return
            dictionary[entry.name] = entry
        else:
            if entry_type == EntryType.Spell:
                dictionary[entry.name].append_spell(entry)
            else:
                dictionary[entry.name].append_source(resource)

    def list(self, entry_type):
        entry_dict = self.entries[entry_type]
        for name in entry_dict:
            print(name)

    def length(self, entry_type):
        return len(self.entries[entry_type])

    def find(self, name, entry_type):
        entry_dict = self.entries[entry_type]
        if name not in entry_dict.keys():
            return None
        else:
            return entry_dict[name]

    def validate_monsters(self):
        print("Validating Monsters")
        self.validate_individual(EntryType.Monster)  # validate database fields
        monsters = self.get_monsters()
        print("Trialing Actions:")
        for monster in monsters.values():
            if not hasattr(monster, "action_list"):
                continue
            for action in monster.action_list:
                if action is None:
                    print("\t! Faulty Action -", monster.name, action.name)
                elif not hasattr(action, "name"):
                    print("\t! Action without name -", monster.name)

    def validate_items(self):
        entries = self.entries[EntryType.Item]
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

    def validate_spells(self):
        print("Validating Spells")
        self.validate_individual(EntryType.Spell)

    def validate_individual(self, entry_type):
        entries = self.entries[entry_type]
        for name, entry in entries.items():
            for req in entry.required_database_fields:
                if not hasattr(entry, req) or getattr(entry, req) is None:
                    print(f"Missing! \"{req}\" in {entry.name}")
