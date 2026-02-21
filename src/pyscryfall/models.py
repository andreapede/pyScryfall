from enum import Enum

class Format(str, Enum):
    """Supported Magic: The Gathering formats."""
    STANDARD = 'standard'
    MODERN = 'modern'
    LEGACY = 'legacy'
    VINTAGE = 'vintage'
    COMMANDER = 'commander'
    PAUPER = 'pauper'
    PIONEER = 'pioneer'
    BRAWL = 'brawl'
    HISTORIC = 'historic'
    PENNY = 'penny'
    ALCHEMY = 'alchemy'
    EXPLORER = 'explorer'
    TIMELESS = 'timeless'

class Rarity(str, Enum):
    """Magic: The Gathering card rarities."""
    COMMON = 'common'
    UNCOMMON = 'uncommon'
    RARE = 'rare'
    MYTHIC = 'mythic'
    SPECIAL = 'special'
    BONUS = 'bonus'
