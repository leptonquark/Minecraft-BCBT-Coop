import numpy as np

from utils.vectors import CIRCLE_DEGREES

SECOND_PER_MS = 0.001


def ms_to_seconds(ms):
    return SECOND_PER_MS * ms


def rad_to_degrees(rad):
    half_circle = CIRCLE_DEGREES / 2
    return rad * half_circle / np.pi