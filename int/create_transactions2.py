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
    "`tx4`	TEXT,"    # Could be an int, but more processing overhead needed for real life use.
    "`public_key`	TEXT,"
    "`block_hash`	TEXT,"
    "`ifee`	INTEGER,"
    "`ireward`	INTEGER,"
    "`operation`	TEXT,"
    "`openfield`	TEXT"
    ")"
)

SQL_INDICES = [
    # Check with queries what of iamount, ireward or ireward, iamount makes more sense (goal: avoid an extra index)
    "CREATE INDEX `Recipient_Index` ON `transactions2` (`recipient`, `iamount`, `ireward`)",
    "CREATE INDEX `Address_Index` ON `transactions2` (`address`, `iamount`, `ifee`)",
    "CREATE INDEX `tx4_Index` ON `transactions2` (`tx4`)",
    # Maybe a "hash4" indexed field could help reduce the size, avoiding a block_hash index. done, yes.
    # better: store block hash as bin, storage and index/2
    # then hash2 to 4 would be enough (and just a big int - int in sqlite are up to 8 bytes long)
    # ninja option: store hash as bin, and split over 2 columns.
    # First one is 4, indexed. Second one remaining 24 bytes, non indexed, as Blob
    # there are no aggregate ops on hash, only lookup of a single one. So no covering index is needed.
    # select count(*) as nb from transactions2 group by bhash4 order by nb desc limit 10;
    # 2 res at 10 per bhash4, 1 from around 200
]

"""
ledger.db:  6 223 858 688
ledgeri.db: 3 822 051 328 (minimal indexes above)

            3 846 848 512 (+ block_height index) - CREATE INDEX `height_Index` ON `transactions2` (`block_height`)
            3 979 751 424 (+ block_hash_index) - CREATE INDEX `hash_Index` ON `transactions2` (`block_hash`)
                            5 228 298 240 (+ signature_index) - CREATE INDEX `signature_Index` ON `transactions2` (`signature`)
                            4 010 049 536 (+ bhash4 and index) - ALTER TABLE transactions2 ADD COLUMN bhash4 INTEGER; CREATE INDEX `bhash4_Index` ON `transactions2` (`bhash4`)
            3 877 146 624 (bhash4, no full block_hash index, current candidate)              

            3 897 917 440 (+ operation index) - CREATE INDEX `operation_Index` ON `transactions2` (`operation`);
            3 996 139 520 (+ openfield index) - CREATE INDEX `openfield_Index` ON `transactions2` (`openfield`);

Overheads
0 024 797 184 Block height index - 25 Mo
1 248 546 816 Full signatures index - 1.2 Go 
0 132 902 912 Full block_hash index - 132 Mo
0 030 298 112 bhash4 + bhash4_index - 30 Mo (so, same as tx4 I guess, 4 bytes)
0 020 770 816 operation index - 20 Mo 
0 098 222 080 openfield index - 98 Mo  -> could be replaced by openfield checksum as int4 (0 if no data) and no index on real column. 
                                          because this one will grow with more openfield usage, and we likely only will support exact match queries on that one by default.
"""

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
    ledger.execute("PRAGMA journal_mode=truncate")
    ledger.execute("PRAGMA page_size = 4096")
    ledger.execute("VACUUM")
    ledger.execute(SQL_CREATE)
    for sql in SQL_INDICES:
        ledger.execute(sql)
    ledger.commit()
    start = time()
    ledger.execute(SQL_COPY)
    ledger.commit()
    print(time() - start, "Seconds")

