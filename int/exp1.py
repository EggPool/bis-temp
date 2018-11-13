"""
Experiment 1

Make sure that mining_reward does **not** need any quantize voodoo
"""


from quantizer import *
import essentials

for block_height_new in range(800000, 1500000):
    # quantize
    mining_reward = 15 - (quantize_eight(block_height_new) / quantize_eight(1000000 / 2)) - Decimal("0.8")
    reward1 = str(quantize_eight(mining_reward))

    # no quantize
    mining_reward = 15 - block_height_new / (1000000 / 2) - 0.8
    reward2 = '{:.8f}'.format(mining_reward)

    # int
    mining_reward = int(15*1e8 - block_height_new*1e8 / (1000000 / 2) - int(0.8*1e8))
    reward3 = essentials.int_to_f8(mining_reward)

    ok = ''
    if reward1 != reward2 :
        ok += '2'
    if reward1 != reward3 :
        ok += '3'
    if ok != '':
        print(ok, reward1, reward2, reward3)
