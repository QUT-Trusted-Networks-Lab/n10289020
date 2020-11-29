import math
import numpy as np
from .Exposure import calculateExposure

def calculateTransProbability(exposure):
    SIGMA = 0.33  # This is for Influenza, needed to be change into Covid-19
    return 1 - math.exp(-SIGMA * exposure)
