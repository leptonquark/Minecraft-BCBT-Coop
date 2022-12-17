from enum import Enum


class Cooperativity(Enum):
    INDEPENDENT = 0
    COOPERATIVE = 1
    COOPERATIVE_WITH_BACKUP = 2
