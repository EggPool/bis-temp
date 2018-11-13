"""
Experiment 5

Check whether diff drop needs decimals

Yes, some because of extra rounding to 2 decimals that is introduced.
Can't remove there without a HF
"""



import essentials
import random
import time
from decimal import *
from quantizer import *

# run one million random tests
K = 1000000

diff_drop_time = 180
difficulty = 100


def diffdrop1(time1, timestamp_last):
    diff_dropped = difficulty
    if Decimal(time1) > Decimal(timestamp_last) + Decimal(2 * diff_drop_time):
        # Emergency diff drop
        time_difference = quantize_two(time1) - quantize_two(timestamp_last)
        diff_dropped = quantize_ten(difficulty) - quantize_ten(1) \
                   - quantize_ten(10 * (time_difference - 2 * diff_drop_time) / diff_drop_time)
    elif Decimal(time1) > Decimal(timestamp_last) + Decimal(diff_drop_time):
        time_difference = quantize_two(time1) - quantize_two(timestamp_last)
        diff_dropped = quantize_ten(difficulty) + quantize_ten(1) - quantize_ten(time_difference / diff_drop_time)
    return "{:.10f}".format(diff_dropped)


def diffdrop2(time1, timestamp_last):
    diff_dropped = difficulty
    if time1 > timestamp_last + 2 * diff_drop_time:
        # Emergency diff drop
        # time_difference = time1 - timestamp_last
        time_difference = quantize_two(time1) - quantize_two(timestamp_last)
        diff_dropped = difficulty - 1 - (10 * (time_difference - 2 * diff_drop_time) / diff_drop_time)
    elif time1 > timestamp_last + diff_drop_time:
        # time_difference = time1 - timestamp_last
        time_difference = quantize_two(time1) - quantize_two(timestamp_last)
        diff_dropped = difficulty + 1 - (time_difference / diff_drop_time)
    return "{:.10f}".format(diff_dropped)


for test in range(K):
    timestamp_last = time.time()
    time1 = timestamp_last + 60 + random.gauss(60, 60)

    res1 = diffdrop1(time1, timestamp_last)

    res2 = diffdrop2(time1, timestamp_last)

    if res1 != res2:
        print("Ko", timestamp_last, time1, res1, res2)


print("Done {} tests".format(K))
