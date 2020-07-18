
from subprocess import Popen, PIPE, TimeoutExpired, run
import subprocess
import platform
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor
from subprocess import TimeoutExpired, PIPE, Popen
import signal
import sys
from multiprocessing.connection import Client, Listener, wait, Pipe
from multiprocessing import Queue, Process, Pool, Process, Lock, Value, Array, Manager

__t_pool = ThreadPoolExecutor()

# os.system()
# os.popen()


def shell(cmd, fn=None):
    print('[ cmd ] ', cmd, end='\n')
    if fn is None:
        run(cmd, shell=True)
    else:
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                   preexec_fn=os.setsid, encoding='utf-8') as pipe:
            try:
                res = pipe.communicate()[0]
                fn(res)
                print("command result : \n%s" % res)
            except TimeoutExpired as e:
                os.killpg(pipe.pid, signal.SIGINT)
                out_bytes = pipe.communicate()[0]
                print('command result : \n%s' % (out_bytes))


def capture_event(serial_no):
    cmd = 'adb -s {}  shell getevent -lp'.format(serial_no)
    ret = os.popen(cmd).readlines()
    xmin = 0.0
    xmax = 0.0
    ymin = 0.0
    ymax = 0.0
    screen_width = 0.0
    screen_height = 0.0

    def get_value(line):
        elems = line.split(',')
        for e in elems:
            if 'min' in e:
                min_str = e.strip().split(" ")[1]
            elif 'max' in e:
                max_str = e.strip().split(" ")[1]
        return (float(min_str), float(max_str))

    for line in ret[1:]:
        if 'ABS_MT_POSITION_X' in line:
            (xmin, xmax) = get_value(line)
        elif 'ABS_MT_POSITION_Y' in line:
            (ymin, ymax) = get_value(line)
    cmd = 'adb -s {}  shell wm size'.format(serial_no)
    ret = os.popen(cmd).readlines()[0].split(':')[1].strip().split('x')
    screen_width = float(ret[0].strip())
    screen_height = float(ret[1].strip())
    # print(xmin, xmax, ymin, ymax, screen_width, screen_height)
    # 360.3336422613531,1997.8537836682342
    cmd = 'adb -s {}  shell getevent -tl'.format(serial_no)
    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
               preexec_fn=os.setsid, encoding='utf-8') as pipe:
        try:
            i = 0
            for line in iter(lambda: pipe.stdout.readline(), ''):
                if 'ABS_MT_POSITION_X' in line:
                    ABS_MT_POSITION_X = line.split(
                        "ABS_MT_POSITION_X")[-1].strip()
                    raw_x = (int(ABS_MT_POSITION_X, 16) - xmin) * \
                        screen_width / (xmax - xmin)
                    # print(ABS_MT_POSITION_X,int(ABS_MT_POSITION_X,16),raw_x)
                    line = line.replace(ABS_MT_POSITION_X, str(raw_x))
                elif 'ABS_MT_POSITION_Y' in line:
                    ABS_MT_POSITION_Y = line.split(
                        "ABS_MT_POSITION_Y")[-1].strip()
                    raw_y = (int(ABS_MT_POSITION_Y, 16) - ymin) * \
                        screen_height / (ymax - ymin)
                    line = line.replace(ABS_MT_POSITION_Y, str(raw_y))
                sys.stdout.write('[{}] {}'.format(i, line))
                i += 1
        except TimeoutExpired as e:
            os.killpg(pipe.pid, signal.SIGINT)
            out_bytes = pipe.communicate()[0]
            print('command error : \n%s' % (out_bytes))
    # server_start(cmd,child_conn,queue)
    # client_start(parent_conn,queue)


def install_app(serial_no, package_name, app_path):
    cmds = [
        "adb -s {} shell am force-stop {}".format(
            serial_no, package_name),
        "adb -s {} install -r -t  {}".format(serial_no, app_path),
        "adb -s {} shell pm grant {} android.permission.READ_EXTERNAL_STORAGE".format(
            serial_no, package_name),
        "adb -s {} shell pm grant {}android.permission.WRITE_EXTERNAL_STORAGE".format(
            serial_no, package_name),
        "adb -s {} shell pm grant {} android.permission.READ_PHONE_STATE".format(
            serial_no, package_name),
        "adb -s {} shell pm grant {} android.permission.ACCESS_FINE_LOCATION".format(
            serial_no, package_name)
    ]

    brand = os.popen("adb -s " + serial_no +
                     "  shell getprop ro.product.brand").readlines()[0].strip()
    if brand == "HUAWEI":
        for cmd in cmds:
            shell(cmd)
    elif brand == "xiaomi":
        for cmd in cmds:
            shell(cmd)
    elif brand == "OPPO":
        def task(cmds):
            for cmd in cmds:
                shell(cmd)

        __t_pool.submit(task, cmds)
        time.sleep(20)
        shell(
            "adb -s {} shell input tap {}".format(serial_no, '799.7405 1892.8088'))
        time.sleep(3)
        # shell(
        #     "adb -s {} shell input tap {}".format(self.serial_no, '360.333 1997.853'))
        time.sleep(30)
        shell("adb -s {} shell input tap {}".format(serial_no,
                                                    '367.3401 2076.8875'))
    elif brand == "vivo":
        def task(cmds):
            for cmd in cmds:
                shell(cmd)
        __t_pool.submit(task, cmds)
        time.sleep(10)
        shell(
            "adb -s {} shell input tap {}".format(serial_no, '360.333 1997.853'))
        time.sleep(3)
        shell(
            "adb -s {} shell input tap {}".format(serial_no, '360.333 1997.853'))
        time.sleep(30)
        shell(
            "adb -s {} shell input tap {}".format(serial_no, '676.6265 2170.9277'))
    print('=====>>>安装完成 %s,%s' % (serial_no, brand))


switch_to_queue = False
parent_conn, child_conn = Pipe()
queue = Queue()
address = ('localhost', 6000)
family = 'AF_UNIX'


def server_start(cmd, child_conn=None, queue=None):
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


def is_python3():
    return sys.version_info[0] == 3


def is_macos():
    return "Darwin" in platform.system()


bar = [
    " [=     ]",
    " [ =    ]",
    " [  =   ]",
    " [   =  ]",
    " [    = ]",
    " [     =]",
    " [    = ]",
    " [   =  ]",
    " [  =   ]",
    " [ =    ]",
]


def print_with_bar(pos, *infos):
    s = ''
    for i in infos:
        s = s+str(i)
    print(bar[pos % len(bar)] + ' ' + s + '\r')
