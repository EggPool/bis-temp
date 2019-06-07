"""
Supposes a bhash4 column of type INTEGER exists, with related index
(index can be created after initial data insert for perf)

Maybe it's possible to do the conversion with sql alone, did not find a straight way, why this slow one by one parsing.
Could be optimized, but it's a one time convert job, then it's done one insert only.

KEPT SAME COLUMN NAME FOR EASE OF TESTING
"""
import sqlite3
from time import time

# Set path to your ledger (copy of ledger.db, or ledger.db itself)
LEDGER_DB = "static/ledgeri.db"

if __name__ == "__main__":
    print(LEDGER_DB)
    ledger = sqlite3.connect(LEDGER_DB)
    ledger.execute("PRAGMA journal_mode=truncate")
    ledger.execute("PRAGMA page_size = 4096")
    start = time()
    res = ledger.execute("SELECT block_height, block_hash from transactions2")
    for height, hash in res.fetchall():
        hash6 = int(hash[:12], 16)
        #print(height, hash, hash4)
        ledger.execute("UPDATE transactions2 SET bhash4 = ? where block_height = ?", (hash6, height))
    ledger.commit()
    print(time() - start, "Seconds")

