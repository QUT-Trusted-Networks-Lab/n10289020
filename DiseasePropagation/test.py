import numpy as np
import math

result = 0.304 * (7.5 / (1000 * 60)) * (math.exp((51923-54480)/1200) - math.exp((51923-56307)/1200) +
                                        math.exp((48024 - 56307)/1200) - math.exp(48024 - 54480))
result = result / (2512 / (1200 ** 2))

print( 1 - math.exp(-0.33*result))