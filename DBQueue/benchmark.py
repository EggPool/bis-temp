from socket import socket
import connections
from time import time
import threading

NUM = 20

def do_A(index: int):
    s = socket()
    s.settimeout(10)
    s.connect(("127.0.0.1", 5555))
    connections.send (s, "storeA")
    connections.send (s, index)
    res = connections.receive(s)
    print(res)


def do_B(index: int):
    s = socket()
    s.settimeout(10)
    s.connect(("127.0.0.1", 5555))
    connections.send (s, "storeB")
    connections.send (s, index)
    res = connections.receive(s)
    print(res)


if __name__ == "__main__":
    start = time()
    print(f"{start} -Start")
    threads = []
    for i in range(NUM):
        thread = threading.Thread(target=do_A, args=(i,))
        threads.append(thread)
    now = time()
    print(f"{now} - {NUM} threads created")
    for t in threads:
        t.start()
    now = time()
    print(f"{now} - All threads started")
    for t in threads:
        t.join()
    now = time()
    print(f"{now} - All threads ended")
    print(f"{now - start} - Total Time A ")

    print("")
    start = time()
    print(f"{start} -Start")
    threads = []
    for i in range(NUM):
        thread = threading.Thread(target=do_B, args=(i,))
        threads.append(thread)
    now = time()
    print(f"{now} - {NUM} threads created")
    for t in threads:
        t.start()
    now = time()
    print(f"{now} - All threads started")
    for t in threads:
        t.join()
    now = time()
    print(f"{now} - All threads ended")
    print(f"{now - start} - Total Time B ")
