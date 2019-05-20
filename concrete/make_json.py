"""
Get json reference data, as sent after a blockscf message
"""

import json
import sqlite3
from os import makedirs
from time import time

LEDGER = '../../Bismuth-temp/static/ledger.db'


def export_to_json(from_block:int, to_block:int, filename:str) -> None:
    count = to_block - from_block + 1
    start = time()
    db = sqlite3.connect(LEDGER)
    blocks = []
    for height in range(from_block, to_block +1):
        # No fee nor reward
        query = 'SELECT timestamp,address,recipient,amount,signature,public_key,operation,openfield FROM transactions ' \
                'WHERE block_height = ?'
        params = (height, )
        res = db.execute(query, params)
        blocks.extend([res.fetchall()])
    #print(blocks)
    with open(filename, 'w') as fp:
        json.dump(blocks, fp)
    print("{} Blocks in {} secs.".format(count, time() - start))

    blocks2 = list()
    for block in blocks:
        block2 = list()
        for tx in block:
            tx = list(tx)
            # Trim to simulate binary ecdsa pubkey adn addresses
            tx[5] = tx[5][:32]
            tx[4] = tx[4][:80]
            block2.append(tx)
        blocks2.append(block2)

    filename = filename.replace('.json', '.ecdsa.json')
    with open(filename, 'w') as fp:
        json.dump(blocks2, fp)


if __name__ == "__main__":
    makedirs('data', exist_ok=True)
    # block 1159901 to 1160000 (100 blocks)
    export_to_json(1160000 - 99, 1160000, "data/b100.json")
    # block 1159001 to 1160000 (1k blocks)
    export_to_json(1160000 - 999, 1160000, "data/b1k.json")
    # block 1150001 to 1160000 (10k blocks)
    export_to_json(1160000 - 9999, 1160000, "data/b10k.json")
    """
    Slow hdd : 
        1st run
            100 Blocks in 0.1 secs.
            1000 Blocks in 0.84 secs.
        2nd run (cached by sqlite)
            100 Blocks in 0.007594968795776367 secs.
            1000 Blocks in 0.058257713317871094 secs.
            10000 Blocks in 0.6318052291870117 secs.
            
        b100 - 360188 Bytes
        b1k  - 3122332 Bytes
        b10k - 34042872 Bytes 32.5Mo - 9461994 gz compressed
        
        32.5 Mo / 10k blocks
        3250 Mo / 1 Mo block
        
        9Mo / 10k blocks
        900Mo / 1Mo Blocks
        
        
        ecdsa : b10k - 5530144 Bytes (5.3Mo) - 1.7Mo gz compressed
    """

