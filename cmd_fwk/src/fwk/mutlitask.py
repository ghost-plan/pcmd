"""
多进程(并行，parallel) 多线程(并发，concurrent)  协程

多进程multiprocessing  多线程concurrent

多进程通信的方式:管道(消息)与共享队列

Keyword arguments:
argument -- description
Return: return_description
"""

from multiprocessing.connection import Client, Listener, wait, Pipe
import socket
from multiprocessing import Queue, Process, Pool, Process, Lock, Value, Array, Manager
import os
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from multiprocessing import Process, Pool
from concurrent.futures import ProcessPoolExecutor
import time
import random
import sys
import os
import queue
import asyncio
import time

# =====================================多进程===============================================================
switch_to_queue = False
parent_conn, child_conn = Pipe()
queue = Queue()
address = ('localhost', 6000)
family = 'AF_UNIX'


def server_start(child_conn=None, queue=None):
    def task(conn):
        print('server side start')
        # if switch_to_queue and queue:
        #     for i in range(0,10):
        #         queue.put('[queue] coming from server side')
        #         time.sleep(1)
        # elif conn:
        #     for i in range(0,10):
        #         conn.send('[pip] coming from server side...{}'.format(i))
        #         time.sleep(0.3)
        #     conn.send('exit')

        with Client(address) as client:
            for i in range(0, 10):
                client.send('push {} msg to client '.format(i))

    p = Process(target=task, args=(child_conn,))
    p.start()
    # p.join()
    # with ProcessPoolExecutor() as proc_exe:
    #     proc_exe.submit(task)


def client_start(conn=None, queue=None):
    print('client side start')
    result = None
    # while True:
    #     if switch_to_queue and queue:
    #         result = queue.get()
    #     elif conn:
    #         result = conn.recv()
    #         print('result:',result)
    #         if 'exit' in result:
    #             break

    with Listener(address) as listener:
        with listener.accept() as conn:
            while True:
                try:
                    ret = conn.recv()
                except EOFError as e:
                    print('error:', e.__cause__)
                    break
                else:
                    print('result:', ret)
    print('client side end')


def task(pos):
    for i in tqdm(range(5), ncols=80, desc='执行任务' + str(pos) + ' pid:' + str(os.getpid())):
        # time.sleep(random.random() * 3)
        time.sleep(1)
        pass


def main():
    CORE_POOL_SIZE = max(2, min(cpu_count() - 1, 4))
    MAXIMUM_POOL_SIZE = cpu_count() * 2 + 1
    print(cpu_count(), CORE_POOL_SIZE, MAXIMUM_POOL_SIZE)
    with Pool(MAXIMUM_POOL_SIZE) as p_pool:
        start = time.time()
        for i in range(0, 1000):
            p_pool.apply_async(task, [i])
        p_pool.close()
        p_pool.join()
        end = time.time()
        print("异步多进程耗时:" + str(end - start))
        start = time.time()
        for i in range(0, 10):
            task(i)
        end = time.time()
        print("同步多进程耗时:" + str(end - start))


# =====================================多线程===============================================================

# =====================================协程===============================================================
async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def entry():
    # 1
    # print(f"started at {time.strftime('%X')}")

    # await say_after(3, 'hello')
    # await say_after(1, 'world')

    # print(f"finished at {time.strftime('%X')}")

    # # 2
    # task1 = asyncio.create_task(
    #     say_after(3, 'hello'))

    # task2 = asyncio.create_task(
    #     say_after(1, 'world'))

    # print(f"started at {time.strftime('%X')}")

    # # Wait until both tasks are completed (should take
    # # around 2 seconds.)
    # await task1
    # await task2

    # print(f"finished at {time.strftime('%X')}")

    async def handle(index):
        if index == 2:
            await asyncio.sleep(2)
        print('index ' + str(index))
        # while True:
        # print('index '+str(index))
        # asyncio.sleep(index)

    for i in range(1, 7):
        asyncio.create_task(handle(i))
    print('cjf')


if __name__ == "__main__":
    main()
    # asyncio.run(entry())
    asyncio.get_event_loop().run_until_complete(entry())
    asyncio.get_event_loop().run_forever()
