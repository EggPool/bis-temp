"""
Experiment 2

Check that  balances are the same with "numeric" or int
"""

import options
import os, sqlite3, sys, time, random
from decimal import *
from quantizer import *
# import essentials
from random import shuffle

# Check every single address balance one by one.
DO_CHECK = True

# Speed benchmark on all addresses, but no check
DO_BENCH1 = False

# speed benchmark on top 100 addresses
DO_BENCH2 = True



# EGG ##########################################"

DECIMAL_1E8 = Decimal(100000000)

# percentage from node.py to throw away
getcontext().rounding = ROUND_HALF_EVEN
# getcontext().prec = 8 # 28 by default


def int_to_f8(an_int: int):
    return str('{:.8f}'.format(Decimal(an_int) / DECIMAL_1E8))


def f8_to_int(a_str: str):
    return int(Decimal(a_str) * DECIMAL_1E8)



print(getcontext())


config = options.Get()
config.read()

# genesis_conf = config.genesis_conf
ledger_path_conf = "static/ledgeri.db"



def db_h_define():
    hdd = sqlite3.connect(ledger_path_conf, timeout=1)
    hdd.text_factory = str
    h = hdd.cursor()
    hdd.execute("PRAGMA page_size = 4096;")
    return hdd, h

def commit(cursor):
    """Secure commit for slow nodes"""
    while True:
        try:
            cursor.commit()
            break
        except Exception as e:
            print("Database cursor: {}".format(cursor))
            print("Database retry reason: {}".format(e))


def execute(cursor, query):
    """Secure execute for slow nodes"""
    while True:
        try:
            cursor.execute(query)
            break
        except Exception as e:
            print("Database query: {} {}".format(cursor, query))
            print("Database retry reason: {}".format(e))
    return cursor


def execute_param(cursor, query, param):
    """Secure execute w/ param for slow nodes"""
    while True:
        try:
            cursor.execute(query, param)
            break
        except Exception as e:
            print("Database query: {} {} {}".format(cursor, query, param))
            print("Database retry reason: {}".format(e))
            time.sleep(random.random())
    return cursor


def balance_from_cursor(cursor, address):
    credit = Decimal("0")
    debit = Decimal("0")
    for entry in execute_param(
        cursor,
        "SELECT amount,reward FROM transactions WHERE recipient = ? ",
        (address,),
    ):
        try:
            # result = cursor.fetchall()
            credit = credit + quantize_eight(entry[0]) + quantize_eight(entry[1])
            # print (result)
            credit = 0 if credit is None else credit
        except Exception as e:
            credit = 0
    if VERBOSE:
        print("Credit1", credit)

    for entry in execute_param(
        cursor, "SELECT amount,fee FROM transactions WHERE address = ? ", (address,)
    ):
        try:
            # result = cursor.fetchall()
            debit = debit + quantize_eight(entry[0]) + quantize_eight(entry[1])
            # print (result)
            debit = 0 if debit is None else debit
        except Exception as e:
            debit = 0
        # print (debit)
    if VERBOSE:
        print("Debit1", debit)

    return "{:.8f}".format(quantize_eight(credit - debit))


def balance_from_intcursor(cursor, address):
    q1 = execute_param(
        cursor,
        "SELECT sum(iamount+ireward) FROM transactions2 WHERE recipient = ? ",
        (address,),
    )
    r1 = q1.fetchone()
    credit = r1[0] if r1[0] else 0
    if VERBOSE:
        print("Credit2", credit)
    q2 = execute_param(
        cursor,
        "SELECT sum(iamount+ifee) FROM transactions2 WHERE address = ? ",
        (address,),
    )
    r2 = q2.fetchone()
    debit = r2[0] if r2[0] else 0
    if VERBOSE:
        print("Debit2", debit)
        print("diff", Decimal(credit - debit))

    return "{:.8f}".format(Decimal(credit - debit) / DECIMAL_1E8)


def check(addresses):
    global ERRORS
    for address in addresses:
        address = address[0]
        balance1 = balance_from_cursor(h, address)
        # balance2 = balance_from_cursor(h2, address)
        balance2 = balance_from_intcursor(h, address)
        if balance1 == balance2:
            check = "  Ok"
        else:
            check = "> Ko"
            ERRORS += 1

        if (
            address.lower() != address
            or len(address) != 56
            and (balance1 or balance2) != 0
        ):
            print(address, "> you dun fukt it up")

        if check == "> Ko":
            print(check, address, balance1, balance2)

        if Decimal(balance1) < 0 or Decimal(balance2) < 0:
            print(address, balance1, balance2)


def bench(addresses):
    start = time.time()
    for address in addresses:
        address = address[0]
        balance1 = balance_from_cursor(h, address)
    print("legacy ", time.time() - start)

    start = time.time()
    for address in addresses:
        address = address[0]
        balance1 = balance_from_intcursor(h, address)
    print("int ", time.time() - start)


if __name__ == "__main__":
    # Hyper
    # hdd2, h2 = db_h2_define()
    # Ledger
    hdd, h = db_h_define()
    ERRORS = 0

    VERBOSE = False

    if DO_CHECK:
        print("Selecting all addresses from full ledger for errors")
        execute(h, ("SELECT distinct(recipient) FROM transactions group by recipient;"))
        result = h.fetchall()

        print("Checking...")
        check(result)
        print("Done, {} Errors.".format(ERRORS))



    """
    # uncomment to benchmark
    bench(result)
    sys.exit()
    """


    # benchmark: top 100 largest addresses, 20 times each
    execute(h, ("SELECT distinct(recipient) FROM transactions group by recipient order by count(*) DESC limit 100"))
    result = h.fetchall()
    temp = []
    for address in result:
        temp.append(address * 20)
    shuffle(temp)
    bench(temp)

