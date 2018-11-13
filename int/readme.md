# Integer experiments

Goal: simplify and ease readability of the code by removing all the decimals and quantize calls.

# Helpers

Decimals only have to appear in 2 functions that have been added to essentials.py

```
DECIMAL_1E8 = Decimal(100000000)

# percentage from node.py to throw away
getcontext().rounding = ROUND_HALF_EVEN
# getcontext().prec = 8 # 28 by default


def int_to_f8(an_int: int):
    return str('{:.8f}'.format(Decimal(an_int) / DECIMAL_1E8))


def f8_to_int(a_str: str):
    return int(Decimal(a_str) * DECIMAL_1E8)
```

We either deal with amounts as :
- string representation of a float, with 8 digits after the decimal (json, core protocol)
- integer, as 1E8 * float amount (internal reprentation, storage, all computations)

The 2 functions are lossless and exact transcriptions from one format to another, with no possible precision loss.

Computation on the integers only ensure there is no possible precision or rounding error, ever.
