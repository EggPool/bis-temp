"""
Experiment 3

Proof that convert functions are bijective
"""


import essentials
import random

digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]

# run one million random tests
K = 1000000

for test in range(K):
    # Create a fake amount with 0.8f
    f8 = '0.' + ''.join([str(i) for i in random.choices(digits, k=8)])

    # convert to int
    int = essentials.f8_to_int(f8)
    # and back to 0.8f
    f8b = essentials.int_to_f8(int)

    # scream if diff.
    if f8 != f8b:
        print("KO", f8, int, f8)

print("Done {} tests".format(K))
