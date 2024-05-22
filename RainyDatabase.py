import json
import logging
import os
import pathlib
from enum import Enum

import xml.etree.ElementTree as ET

import requests

from .entry import EntryType
from .sw5e import DatabaseRESTAPI


class System(Enum):
    DnD5e = "DnD5e"
    SW5e = "SW5e"


class RainyDatabase:
    """
    SW5e content can be accessed from their database using the link
    "https://sw5eapi.azurewebsites.net/api/[query]"
    Where query can have the following values:
- archetype
- armorProperty
- background
- class
- conditions
- enhancedItem
- equipment
- feat
- feature
- fightingMastery
- fightingStyle
- lightsaberForm
- monster
- power
- referenceTable
- skills
- species
- starshipDeployment
- starshipEquipment
- starshipModification
- starshipBaseSize
- starshipVenture
- weaponProperty
- ClassImprovement
- MulticlassImprovement
- SplashclassImprovement
- WeaponFocus
- WeaponSupremacy
- PlayerHandbookRule
- StarShipRule
- VariantRule
- WretchedHivesRule
    """

    valid_spells = None
    valid_items = None
    valid_monsters = None

    def __init__(
            self,
            system: System,
            system_entry_classes: dict,
            path: str = None
    ):
        self.system = system
        self.system_entry_classes = system_entry_classes
        self.path = path
        self.entries = {}
        self.load_resources(path)

    def create_srd_list(self, path):
        if self.system is System.DnD5e:
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

    def get(self, entry_type):
        return self.entries.get(entry_type, [])

    def load_resources(self, path: pathlib.Path):
        for entry_type, entry_class in self.system_entry_classes.items():
            if self.system is System.DnD5e:
                if entry_type is EntryType.Power:
                    _path = path / "5" / "Spells"
                elif entry_type is EntryType.Monster:
                    _path = path / "5" / "Bestiary"
                elif entry_type is EntryType.Item:
                    _path = path / "5" / "Items"
                self.load_xml_entries(_path, entry_type, entry_class)
            if self.system is System.SW5e:
                rest_json_entries = requests.get(DatabaseRESTAPI[entry_type])
                entries = json.loads(rest_json_entries.content.decode())
                self.entries[entry_type] = {entry['name']: entry_class(**entry) for entry in entries}

    def list(self, entry_type):
        entry_dict = self.entries[entry_type]
        for name in entry_dict:
            logging.info(name)

    def length(self, entry_type):
        return len(self.entries[entry_type])

    def find(self, name, entry_type):
        entry_dict = self.entries[entry_type]
        if name not in entry_dict.keys():
            return None
        else:
            return entry_dict[name]

    def load_xml_entries(self, path, entry_type, entry_class):
        path = pathlib.Path(path)
        logging.info(f"Loading resources from {path}")
        for file in path.rglob("*.xml"):
            logging.debug(f"Loading {file}")
            file_entries = self.parse_xml_entries(file, entry_class)
            if entry_type not in self.entries:
                self.entries[entry_type] = file_entries
            else:
                self.entries[entry_type].update(file_entries)

    def parse_xml_entries(self, file: str, entry_class) -> list:
        tree = ET.parse(file)
        root = tree.getroot()
        entries = {}
        for xml_entry in root:
            entry = entry_class(xml_entry)
            entries[entry.get_name()] = entry
        return entries
