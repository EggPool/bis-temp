"""
Experiment 4

Check wether diff needs decimals
"""



import options
import os, sqlite3, sys,  time, random
import math
from decimal import *
from quantizer import *
import essentials
from random import shuffle

print(getcontext())


config = options.Get()
config.read()

genesis_conf = config.genesis_conf
ledger_path_conf = config.ledger_path_conf


def db_h_define():
    hdd = sqlite3.connect(ledger_path_conf, timeout=1)
    hdd.text_factory = str
    h = hdd.cursor()
    hdd.execute("PRAGMA page_size = 4096;")
    return hdd, h


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



def difficulty(c, block_height):
    """ Node diff function for a given blockheight"""
    global timestamp_last
    global timestamp_before_last
    global timestamp_1441
    global timestamp_1440
    global diff_block_previous

    try:

        execute_param(c, "SELECT * FROM transactions WHERE reward != 0 AND block_height <= ? ORDER BY block_height DESC LIMIT 2", (block_height,))
        result = c.fetchone()
        timestamp_last = Decimal(result[1])
        block_height = int(result[0])
        previous = c.fetchone()
        # Failsafe for regtest starting at block 1}
        timestamp_before_last = timestamp_last if previous is None else Decimal(previous[1])

        execute_param(c, ("SELECT timestamp FROM transactions WHERE CAST(block_height AS INTEGER) > ? AND reward != 0 ORDER BY timestamp ASC LIMIT 2"), (block_height - 1441,))
        timestamp_1441 = Decimal(c.fetchone()[0])
        block_time_prev = (timestamp_before_last - timestamp_1441) / 1440
        temp = c.fetchone()
        timestamp_1440 = timestamp_1441 if temp is None else Decimal(temp[0])
        block_time = Decimal(timestamp_last - timestamp_1440) / 1440
        execute_param(c, "SELECT difficulty FROM misc WHERE block_height = ?", (block_height,))
        diff_block_previous = Decimal(c.fetchone()[0])

        time_to_generate = timestamp_last - timestamp_before_last

        hashrate = pow(2, diff_block_previous / Decimal(2.0)) / (
            block_time * math.ceil(28 - diff_block_previous / Decimal(16.0)))
        # Calculate new difficulty for desired blocktime of 60 seconds
        target = Decimal(60.00)
        ##D0 = diff_block_previous
        difficulty_new = Decimal((2 / math.log(2)) * math.log(hashrate * target * math.ceil(28 - diff_block_previous / Decimal(16.0))))
        # Feedback controller
        Kd = 10
        difficulty_new = difficulty_new - Kd * (block_time - block_time_prev)
        diff_adjustment = (difficulty_new - diff_block_previous) / 720  # reduce by factor of 720

        if diff_adjustment > Decimal(1.0):
            diff_adjustment = Decimal(1.0)

        difficulty_new_adjusted = quantize_ten(diff_block_previous + diff_adjustment)
        difficulty = difficulty_new_adjusted

        diff_drop_time = Decimal(180)

        diff_dropped = difficulty
        """
        if Decimal(time.time()) > Decimal(timestamp_last) + Decimal(2*diff_drop_time):
            # Emergency diff drop
            time_difference = quantize_two(time.time()) - quantize_two(timestamp_last)
            diff_dropped = quantize_ten(difficulty) - quantize_ten(1) \
                           - quantize_ten(10 * (time_difference-2 * diff_drop_time) / diff_drop_time)
        elif Decimal(time.time()) > Decimal(timestamp_last) + Decimal(diff_drop_time):
            time_difference = quantize_two(time.time()) - quantize_two(timestamp_last)
            diff_dropped = quantize_ten(difficulty) + quantize_ten(1) - quantize_ten(time_difference / diff_drop_time)
        """

        if difficulty < 50:
            difficulty = 50
        if diff_dropped < 50:
            diff_dropped = 50

        return (
            float('%.10f' % difficulty), float('%.10f' % diff_dropped), float(time_to_generate), float(diff_block_previous),
            float(block_time), float(hashrate), float(diff_adjustment),
            block_height)  # need to keep float here for database inserts support

    except Exception as e:
        print("error: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def difficulty2(c, block_height):
    """ Node diff function for a given blockheight"""
    global timestamp_last
    global timestamp_before_last
    global timestamp_1441
    global timestamp_1440
    global diff_block_previous

    try:

        block_time_prev = (timestamp_before_last - timestamp_1441) / 1440
        block_time = (timestamp_last - timestamp_1440) / 1440

        time_to_generate = timestamp_last - timestamp_before_last

        hashrate = pow(2, diff_block_previous / 2) / (
            block_time * math.ceil(28 - diff_block_previous / 16.0))
        # Calculate new difficulty for desired blocktime of 60 seconds
        target = 60
        ##D0 = diff_block_previous
        difficulty_new = (2 / math.log(2)) * math.log(hashrate * target * math.ceil(28 - diff_block_previous / 16))
        # Feedback controller
        Kd = 10
        difficulty_new = difficulty_new - Kd * (block_time - block_time_prev)
        diff_adjustment = (difficulty_new - diff_block_previous) / 720  # reduce by factor of 720

        if diff_adjustment > 1:
            diff_adjustment = 1.0

        difficulty_new_adjusted = diff_block_previous + diff_adjustment
        difficulty = difficulty_new_adjusted

        diff_drop_time = 180

        diff_dropped = difficulty
        """
        if Decimal(time.time()) > Decimal(timestamp_last) + Decimal(2*diff_drop_time):
            # Emergency diff drop
            time_difference = quantize_two(time.time()) - quantize_two(timestamp_last)
            diff_dropped = quantize_ten(difficulty) - quantize_ten(1) \
                           - quantize_ten(10 * (time_difference-2 * diff_drop_time) / diff_drop_time)
        elif Decimal(time.time()) > Decimal(timestamp_last) + Decimal(diff_drop_time):
            time_difference = quantize_two(time.time()) - quantize_two(timestamp_last)
            diff_dropped = quantize_ten(difficulty) + quantize_ten(1) - quantize_ten(time_difference / diff_drop_time)
        """

        if difficulty < 50:
            difficulty = 50
        if diff_dropped < 50:
            diff_dropped = 50

        return (
            float('%.10f' % difficulty), float('%.10f' % diff_dropped), float(time_to_generate), float(diff_block_previous),
            float(block_time), float(hashrate), float(diff_adjustment),
            block_height)  # need to keep float here for database inserts support

    except Exception as e:
        print("error: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def check():
    global timestamp_last
    global timestamp_before_last
    global timestamp_1441
    global timestamp_1440
    global diff_block_previous
    for block in range(231560, 231560+100000):
        diff1 = difficulty(h, block)
        timestamp_last = float(timestamp_last)
        timestamp_before_last = float(timestamp_before_last)
        timestamp_1441 = float(timestamp_1441)
        timestamp_1440 = float(timestamp_1440)
        diff_block_previous = float(diff_block_previous)
        diff2 = difficulty2(h, block)
        if diff1[0] != diff2[0]:
            print("{}: {} {}".format(block, diff1[0], diff2[0]))


if __name__ == "__main__":
    # Ledger
    hdd, h = db_h_define()
    ERRORS = 0

    VERBOSE = False

    print("Selecting blocks from 231560")
    # execute(h, ("SELECT distinct(recipient) FROM transactions2 group by recipient;"))
    # result = h.fetchall()
    check()
