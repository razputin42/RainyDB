from enum import Enum


class EntryType(Enum):
    Monster = "monster"
    Spell = "spell"
    Item = "item"
    Power = "power"


class Entry:
    def __init__(self, **kwargs):
        self.attributes = kwargs
