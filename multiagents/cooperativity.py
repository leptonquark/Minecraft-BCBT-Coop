from enum import Enum


class Cooperativity(Enum):
    INDEPENDENT = 0
    COOPERATIVE = 1
    COOPERATIVE_WITH_CATCHUP = 2

    def __str__(self):
        return names[self]

    def __repr__(self):
        return str(self)


names = {
    Cooperativity.INDEPENDENT: 'Independent',
    Cooperativity.COOPERATIVE: 'Cooperative',
    Cooperativity.COOPERATIVE_WITH_CATCHUP: 'Cooperative with catchup',
}
