# DBQueue

POC/Benchmark: Use a queue and a single DB thread instead of one instance per thread


- run either server.py or server-process.py in one shell
- run benchmark.py in another one.

## server.py

- One single thread waits for a message to be inserted in a queue, processes it.
- every message comes with a queue object to insert the response in.

## server-process.py

- same logic as server, but the worker is a process, not a thread.
- uses multiprocessing.Manager() to handle a cross process Queue
- slower if no cpu intensive task, faster if task is cpu intensive.
