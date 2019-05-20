"""
Get json reference data, compact protobuf format
"""

import base64
import json
import sqlite3
import sys
from os import makedirs
from time import time

import blocks_pb2
import f8int

LEDGER = '../../Bismuth-temp/static/ledger.db'


def export_to_json(from_block:int, to_block:int, filename:str) -> None:
    count = to_block - from_block + 1
    start = time()
    db = sqlite3.connect(LEDGER)
    # No fee nor reward
    """
    query = 'SELECT block_height, timestamp,address,recipient,amount,signature,public_key,operation,openfield FROM transactions ' \
            'WHERE block_height >= ? AND block_height <= ?'
    params = (from_block, to_block)
    res = db.execute(query, params)
    """
    proto_blocks = blocks_pb2.Blocks()
    proto_blocks.Clear()
    blocks = []
    proto_blocks.from_block = from_block
    proto_blocks.to_block = to_block
    for height in range(from_block, to_block +1):
        # No fee nor reward
        query = 'SELECT timestamp,address,recipient,amount,signature,public_key,operation,openfield FROM transactions ' \
                'WHERE block_height = ?'
        params = (height, )
        res = db.execute(query, params)
        blocks.extend([res.fetchall()])
    # stack addresses
    addresses = []
    address_index = {}
    pubkeys = []
    # process sender addresses
    blocks2 = list()
    addresses_count = 0
    for block in blocks:
        block2 = list()
        for tx in block:
            tx = list(tx)
            index = address_index.get(tx[1], -1)
            if index < 0:
                # unknown address ,add
                # addresses.append(tx[1])
                proto_address = proto_blocks.addresses.add()
                proto_address.address = tx[1]
                # We could go one step further by trimming --- BEGIN PUBLIC KEY ---- and b64 decoding again.
                # 20% min gain, but more processing
                pubkey = base64.b64decode(tx[5])
                # pubkeys.append(pubkey)
                proto_pubkey = proto_blocks.pubkeys.add()
                # proto_pubkey.pubkey = pubkey[:32]
                proto_pubkey.pubkey = pubkey
                index = addresses_count
                addresses_count += 1
                address_index[tx[1]] = index
                tx[1] = index  # replace address by index
                tx[5] = ''
            else:
                tx[1] = index  # replace address by index
                tx[5] = ''
            block2.append(tx)
        blocks2.append(block2)
    # process recipient addresses
    for block in blocks2:
        proto_block = proto_blocks.blocks.add()
        for tx in block:
            proto_tx = proto_block.txs.add()
            index = address_index.get(tx[2], -1)
            if index < 0:
                # unknown recipient ,add
                # addresses.append(tx[2])
                proto_address = proto_blocks.addresses.add()
                proto_address.address = tx[2]
                index = addresses_count
                addresses_count += 1
                address_index[tx[2]] = index
                tx[2] = index  # replace address by index
            else:
                tx[2] = index  # replace address by index
            # print(tx)
            proto_tx.timestamp = int(100 * tx[0])
            proto_tx.address_index = tx[1]
            proto_tx.recipient_index = tx[2]
            proto_tx.amount = f8int.f8_to_int(tx[3])
            proto_tx.signature = base64.b64decode(tx[4])
            # proto_tx.signature = base64.b64decode(tx[4])[:80]
            proto_tx.operation = tx[6]
            proto_tx.openfield = tx[7]


    # print(blocks2)
    # print(proto_blocks.SerializeToString())

    # with open(filename, 'w') as fp:
    #     json.dump(blocks2, fp)
    filename = filename.replace('.json', '.pb')
    with open(filename, 'wb') as fp:
        fp.write(proto_blocks.SerializeToString())

    print("{} Blocks in {} secs.".format(count, time() - start))


if __name__ == "__main__":
    makedirs('data', exist_ok=True)
    # export_to_json(1160000 - 9, 1160000, "data/b100_proto.json")
    # sys.exit()
    # block 1159901 to 1160000 (100 blocks)
    export_to_json(1160000 - 99, 1160000, "data/b100_proto.json")
    # block 1159001 to 1160000 (1k blocks)
    export_to_json(1160000 - 999, 1160000, "data/b1k_proto.json")
    # block 1150001 to 1160000 (10k blocks)
    export_to_json(1160000 - 9999, 1160000, "data/b10k_proto.json")



    """
    Slow hdd : 
        2nd run (cached by sqlite)
            100 Blocks in 0.0064 secs.
            1000 Blocks in 0.0529 secs.
            10000 Blocks in 0.548
            
        b100 - 121406 Bytes
        b1k  - 980506 Bytes
        b10k - 10287220 Bytes (9.8Mo) - 9432473 gz compressed
            
        9.8Mo / 10k blocks
        980Mo / 1Mo Blocks            
                
        ecdsa : b10k - 2651930 Bytes (2.5Mo) - 1.7Mo gz comrpessed

        2.5Mo / 10k blocks
        250Mo / 1Mo Blocks            
        

    """

