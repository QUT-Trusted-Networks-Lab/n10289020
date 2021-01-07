import math
import numpy as np
from .Exposure import calculateExposure

def calculateTransProbability(exposure, r_value):
    SIGMA = r_value  # R value for Covid-19
    return 1 - math.exp(-SIGMA * exposure)
