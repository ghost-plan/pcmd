import os
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from multiprocessing import Process,Pool
from concurrent.futures import ProcessPoolExecutor
import time
import random
import sys,os
import queue

def task(pos):
    for i in tqdm(range(5), ncols=80, desc='执行任务' + str(pos) + ' pid:' + str(os.getpid())):
        # time.sleep(random.random() * 3)
        time.sleep(1)
        pass

def  main():
    task_q=queue.SimpleQueue()
    task_q.put()
    CORE_POOL_SIZE = max(2, min(cpu_count() - 1, 4))
    MAXIMUM_POOL_SIZE = cpu_count() * 2 + 1
    print(cpu_count(),CORE_POOL_SIZE, MAXIMUM_POOL_SIZE)
    with Pool(MAXIMUM_POOL_SIZE) as p_pool:
        start = time.time()
        for i in range(0,1000):
            p_pool.apply_async(task, [i])
        p_pool.close()
        p_pool.join()
        end = time.time()
        print("异步多进程耗时:"+str(end-start))
        start = time.time()
        for i in range(0, 10):
            task(i)
        end = time.time()
        print("同步多进程耗时:"+str(end-start))


if __name__ == "__main__":
    main()
    
  
