"""
Alternative server, with the worker in a process of its own instead of a thread.
Uses Manager to proxify the Queue object between processes.
Slower than threading, but would be faster if required job is cpu hungry (1 full core)
"""

import threading
import socketserver
import time
from multiprocessing import Process, Manager

from connections import send, receive


LOCK = threading.Lock()
DB_QUEUE = Manager().Queue()

# Simulate some processing
DELAY = 0.1


def store_a(number: int) -> float:
    with LOCK:
        with open("storeA.txt", "a") as f:
            f.write(f"{number}\n")
            time.sleep(DELAY)
    return time.time()


def store_b(number: int) -> float:
    # We create a queue each time (here, one client = 1 command)
    # But we could maintain a dict indexed with threading id to have a single queue per client until it disconnects.
    local_queue = Manager().Queue()
    item = (local_queue, number)
    DB_QUEUE.put(item)
    # get() blocks until there is an answer. Can take a timeout.
    return local_queue.get()


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            peer_ip = self.request.getpeername()[0]
        except:
            print("Inbound: Transport endpoint was not connected")
            return

        threading.current_thread().name = f"in_{peer_ip}"

        timeout_operation = 120  # timeout
        timer_operation = time.time()  # start counting

        while True:
            try:
                # Failsafe
                if self.request == -1:
                    raise ValueError(f"Inbound: Closed socket from {peer_ip}")

                data = receive(self.request)

                print(
                    f"Inbound: Received: {data} from {peer_ip}"
                )  # will add custom ports later

                if data == "storeA":
                    # StoreA locks file and append from that thread
                    data = receive(self.request)
                    res = store_a(data)
                    send(self.request, res)
                if data == "storeB":
                    # StoreB pushes into a queue.
                    data = receive(self.request)
                    res = store_b(data)
                    send(self.request, res)
                else:
                    if data == "*":
                        raise ValueError("Broken pipe")

                if not time.time() <= timer_operation + timeout_operation:
                    timer_operation = time.time()  # reset timer
                # time.sleep(float(node.pause))  # prevent cpu overload
                print(f"Server loop finished for {peer_ip}")

            except Exception as e:

                print(f"Inbound: Lost connection to {peer_ip}")
                print(f"Inbound: {e}")
                return

        return


# client thread
# if you "return" from the function, the exception code will node be executed and client thread will hang


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def db_thread_loop():
    while True:
        try:
            item = DB_QUEUE.get(block=True, timeout=30)
            # item is a tuple: Queue, data
            print(f"DB Queue got {item}")
            with open("storeB.txt", "a") as f:
                f.write(f"{item[1]}\n")
            DB_QUEUE.task_done()
            time.sleep(DELAY)
            # Send the data back to the provided queue
            item[0].put(time.time())
        except:
            print("DB Process running")


if __name__ == "__main__":
    # cleanup test files
    # os.remove("storeA.txt")
    with open("storeA.txt", "w+") as f:
        f.write("")
    # os.remove("storeB.txt")
    with open("storeB.txt", "w+") as f:
        f.write("")

    # Port 0 means to select an arbitrary unused port
    host, port = "0.0.0.0", 5555

    ThreadedTCPServer.allow_reuse_address = True
    ThreadedTCPServer.daemon_threads = True
    ThreadedTCPServer.timeout = 60
    ThreadedTCPServer.request_queue_size = 100

    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    db_process = Process(target=db_thread_loop)
    db_process.daemon = False
    db_process.start()
    print("Status: DB loop running.")

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print("Status: Server loop running.")

    while True:
        time.sleep(1)
    print("Closed")
