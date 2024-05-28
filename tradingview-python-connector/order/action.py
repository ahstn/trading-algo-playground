from enum import Enum


class Action(str, Enum):
    BUY = "buy"
    SELL = "sell"

    @classmethod
    def _missing_(cls, name):
        """Ensure casing is converted correctly to enum"""
        value = name.lower()
        return cls._value2member_map_.get(value)
