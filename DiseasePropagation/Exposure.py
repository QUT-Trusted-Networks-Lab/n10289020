###### This calculates the Exposure
import numpy as np

def calculateExposure(aer, HSt, HEnd, NbSt, NbEnd):
    a = float(HSt)  ## an individual having disease (infected) arrive in a location. This is the starting time.
    b = float(HEnd)  ## the infected individual left the location
    c = float(NbSt)  ## a sussceptible individual arrived in the same location. This is the arrival time of succeptible
    d = float(NbEnd)  ## This is the time sussceptible left the location
    ta = int((b - a) / 300) + 1  ## this is the time infected stayed in the location. b-a gives in second. division by 300 gives time in 5 minutes.
    ta = ta * 300  ## It is again converted into second as a stay period should be at least 5 minutes.
    tc = int((c - a) / 300)  ## time delay
    tc = tc * 300
    td = int((d - c) / 300) + 1  ## link duration - stay duration
    td = td * 300

    if (d < a):
        return (0)

    ## These are the constant parameters in the disease model
    ## Thsese are discussed  in my published paper
    g = 0.7  ## particle generation rate in pfu - it is calculated for influenza disease
    q = 9 / (1000 * 60)  ## pulmonary rate -- this for human -- how much air a human inhaled
    v = 3.14 * 20 * 20 * 2  ## volume of the proximity -- this is the volume of air in the proximity - pi*r^2*h - r - radious, h height. It is considered as a cylinder of space.
    a = getAer(aer)  ## replaced per our - air in the space is not constant. It is changed over time. This is the rate of change of air. It is randomly generated as different place has different rates.
    r = a / (60 * 60)  ## a was in hourly rates. converting to minutes.

    ## This is the exposure or infectious materials an individual inhale for ta, tc, td time parameters
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
    air = 0
    rsv_air = 0
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

if __name__ == '__main__':
    print(getAer(1))