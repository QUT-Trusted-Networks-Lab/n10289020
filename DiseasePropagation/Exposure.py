###### This calculates the Exposure
import numpy as np

def calculateExposure(aer, HSt, HEnd, NbSt, NbEnd):
    a = float(HSt)
    b = float(HEnd)
    c = float(NbSt)
    d = float(NbEnd)
    ta = int((b - a) / 300) + 1  ## active period
    ta = ta * 300
    tc = int((c - a) / 300)  ## time delay
    tc = tc * 300
    td = int((d - c) / 300) + 1  ## link duration
    td = td * 300

    if (d < a):
        return (0)

    g = 0.68  ## particle generation rate in pfu
    q = 9 / (1000 * 60)  ## pulmonary rate
    v = 3.14 * 20 * 20 * 2  ## volume of the proximity
    a = getAer(aer)  ## replaced per our
    r = a / (60 * 60)

    ea = np.exp(-ta * r)
    ec = np.exp(-tc * r)
    ed = np.exp(-td * r)
    expd = 0
    expi = 0

    if ((tc + td) <= ta):
        comp = ec * (ed - 1) / r
        expd = g * q * (td + comp) / (r * v)

    elif (tc >= ta):
        eacd = np.exp(-(tc + td - ta) * r)
        eca = np.exp(-(tc - ta) * r)
        expi = g * q * (1 - ea) * (eca - eacd) / (r * r * v)
    else:
        eacd = np.exp(-(tc + td - ta) * r)
        comp = (ea - ec) / r
        expd = g * q * (ta - tc + comp) / (r * v)
        expi = g * q * (1 - ea) * (1 - eacd) / (r * r * v)

    exp = expd + expi
    return exp


def getAer(aer):
    '''
    Pick up AER from uniform distribution
    :param aer: Air exchange rate
    :return: Actual Air exchange rate
    '''
    rsv_air = 0
    air = 0
    for i in range(0, 100):
        val = np.random.uniform(0.2, 8)

        if (rsv_air < aer):
            if (val >= aer):
                rsv_air = val
                air = val
                break
        else:
            if (val <= aer):
                rsv_air = val
                air = val
                break
    if (air == 0):
        air = aer
    return (air)
