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
- integer, as 1E8 * float amount (internal representation, storage, all computations)

The 2 functions are lossless and exact transcriptions from one format to another, with no possible precision loss.

Computation on the integers only ensure there is no possible precision or rounding error, ever.

# Experiments and proofs

Files to be put in a working bismuth node.

## exp1.py

Proof that mining_reward does **not** need any quantize voodoo and can be computed as default python float (ie: double) or derived from integer, with the exact same required .8f result.

## exp2.py

Needs a converted db, with "transaction2" table and iamount, ifee, ireward fields (see create_transactions2.py)

- proof that balances are strictly the same for all addresses when using integer as internal representation
- proof that balance check code is simpler and more easily readable - still can be simplified
- benchmark showing also significant speed improvement (the more the address is used, the more the gain)

(copy to Bismuth dir)

## exp3.py

Proof that convert functions are bijective, and that no precision is lost when converting to INT then back to .8f

## exp4.py

Checks whether diff needs decimals (does not)

## exp5.py

Check whether diff drop needs decimals (needs .2f rounding to stay compatible with current values, would not need if rounding is removed after a HF)

## create_transactions2.py

Converts a current ledger.db into a new test format.
In fact, adds an extra "transactions2" table, cloned from transactions, with a few changes:
- all amounts are converted and stored as integer
- an extra 'tx4' indexed filed is added, with 4 first chars of the signature.  
This is to greatly speed up individual tx lookups 
- only 3 indices are setup to limit overweight

- start from a clean ledger.db, vacuum to thereis no extra .wal, .shm files.
- copy the db to ledgeri.db
- run the script to convert (copy to Bismuth dir)

Do not run on a working node, or the transactions/transactions2 will not be in sync and tests will fail.
