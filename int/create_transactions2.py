"""
Creates a "transactions2" table, dup of "transactions but integer amounts, and only minimal indices
"""
import sqlite3
from time import time

# Set path to your ledger (copy of ledger.db, or ledger.db itself)
LEDGER_DB = "static/ledgeri.db"


SQL_CREATE = (
    "CREATE TABLE 'transactions2' ("
    "`block_height`	INTEGER,"
    "`timestamp`	NUMERIC,"
    "`address`	TEXT,"
    "`recipient`	TEXT,"
    "`iamount`	INTEGER,"
    "`signature`	TEXT,"
    "`tx4`	TEXT,"    
    "`public_key`	TEXT,"
    "`block_hash`	TEXT,"
    "`ifee`	INTEGER,"
    "`ireward`	INTEGER,"
    "`operation`	TEXT,"
    "`openfield`	TEXT"
    ")"
)

SQL_INDICES = [
    "CREATE INDEX `Recipient_Index` ON `transactions2` (`recipient`)",
    "CREATE INDEX `Address_Index` ON `transactions2` (`address`)",
    "CREATE INDEX `tx4_Index` ON `transactions2` (`tx4`)",
]

SQL_COPY = "INSERT INTO transactions2(" \
           "block_height, timestamp, address, recipient, " \
           "iamount, signature, tx4, public_key, block_hash, " \
           "ifee, ireward, operation, openfield" \
           ") SELECT block_height, timestamp, address, recipient, " \
           "ROUND(amount*1e8), " \
           "signature, substr(signature,1,4), public_key, block_hash, " \
           "ROUND(fee*1e8), ROUND(reward*1e8), " \
           "operation, openfield FROM transactions"  #  where block_height < 10 and block_height > -10"


if __name__ == "__main__":
    print(LEDGER_DB)
    ledger = sqlite3.connect(LEDGER_DB)
    ledger.execute("PRAGMA page_size = 4096")
    ledger.execute(SQL_CREATE)
    for sql in SQL_INDICES:
        ledger.execute(sql)
    ledger.commit()
    start = time()
    ledger.execute(SQL_COPY)
    ledger.commit()
    print(time() - start, "Seconds")

