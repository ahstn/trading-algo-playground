from enum import Enum


class Position(str, Enum):
    FLAT = "flat"
    SHORT = "short"
    LONG = "long"

    @classmethod
    def _missing_(cls, name):
        """Ensure casing is converted correctly to enum"""
        value = name.lower()
        return cls._value2member_map_.get(value)
