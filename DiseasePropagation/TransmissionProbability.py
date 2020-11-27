import math
import numpy as np
from .Exposure import calculateExposure

def calculateTransProbability(HSt, HEnd, NbSt, NbEnd):
    aer = 60/5
    SIGMA = 0.33  # This is for Influenza, needed to be change into Covid-19
    exposure = calculateExposure(aer, HSt, HEnd, NbSt, NbEnd)
    return 1 - math.exp(-SIGMA * exposure)


if __name__ == '__main__':
    print(calculateTransProbability(1347848024.0,1347851923.0,1347854480.0,1347856307.0))

    pass
