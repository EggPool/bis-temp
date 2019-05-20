
from decimal import Decimal, getcontext, ROUND_HALF_EVEN


DECIMAL_1E8 = Decimal(100000000)

# percentage from node.py to throw away
getcontext().rounding = ROUND_HALF_EVEN
# getcontext().prec = 8 # 28 by default


def int_to_f8(an_int: int):
    return str('{:.8f}'.format(Decimal(an_int) / DECIMAL_1E8))


def f8_to_int(a_str: str):
    return int(Decimal(a_str) * DECIMAL_1E8)

