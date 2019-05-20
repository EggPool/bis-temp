

node can get several blocks at once from peer after "blockscf" confirmation.
this is slow. (to assemble and send): blocks are appended one by one by many queries 

while sys.getsizeof(
   str(blocks_fetched)) < 500000: # limited size based on txs in blocks


 db_handler_instance.execute_param(db_handler_instance.h, (
                                            "SELECT timestamp,address,recipient,amount,signature,public_key,operation,openfield FROM transactions WHERE block_height > ? AND block_height <= ?;"),
(str(int(client_block)), str(int(client_block + 1)),))
double - unnecessary - type conversion


-----
 send(self.request, "blocksfnd")

                                    confirmation = receive(self.request)

                                    if confirmation == "blockscf":
                                        node.logger.app_log.info("Inbound: Client confirmed they want to sync from us")
send(self.request, blocks_fetched)

=> we take time to assemble them, and only after, w ask the peer if he wants them.
if he says no, we did it for nothing.
