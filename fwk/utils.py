
from subprocess import PIPE, TimeoutExpired, run
import subprocess
import platform
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor
import signal
import sys
from multiprocessing.connection import Client, Listener, wait, Pipe
from multiprocessing import Queue, Process, Pool, Process, Lock, Value, Array, Manager
from fwk import compat
__t_pool = ThreadPoolExecutor()

# os.system()
# os.popen()


def shell(cmd, fn=None):
    print('[ cmd ] ', cmd, end='\n')
    if fn is None:
        run(cmd, shell=True)
    else:
        with compat.popen(cmd) as pipe:
            try:
                res = pipe.communicate()[0]
                fn(res)
                print("command result : \n%s" % res)
            except TimeoutExpired as e:
                os.killpg(pipe.pid, signal.SIGINT)
                out_bytes = pipe.communicate()[0]
                print('command result : \n%s' % (out_bytes))


addDeviceLine = """add device \d+: (.+)"""
eventTypeLine = """    [A-Z]+ \((\d+)\): .*"""
eventLine = """(/dev/input/[^:]+): ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)"""

""" 
 backup [-user USER_ID] [-f FILE] [-apk|-noapk] [-obb|-noobb] [-shared|-noshared]
        [-all] [-system|-nosystem] [-keyvalue|-nokeyvalue] [PACKAGE...]
     write an archive of the device's data to FILE [default=backup.adb]
     package list optional if -all/-shared are supplied
     -user: user ID for which to perform the operation (default - system user)
     -apk/-noapk: do/don't back up .apk files (default -noapk)
     -obb/-noobb: do/don't back up .obb files (default -noobb)
     -shared|-noshared: do/don't back up shared storage (default -noshared)
     -all: back up all installed applications
     -system|-nosystem: include system apps in -all (default -system)
     -keyvalue|-nokeyvalue: include apps that perform key/value backups.
         (default -nokeyvalue)
 restore [-user USER_ID] FILE       restore device contents from FILE
     -user: user ID for which to perform the operation (default - system user)
"""
# backup nonsystem apk
# adb backup -apk -shared -nosystem -all -f backup_apk.ab

# backup system and nonsystem apk
# adb backup -apk -noshared -system -all -f backup_apk.ab

# backup individual apk
# adb backup -apk -shared -nosystem -f testing.ab  -keyvalue com.hawksjamesf.spacecraft.debug
# adb backup -apk -shared -nosystem -f testing.ab  -keyvalue com.sankuai.meituan

# restore all
# adb restore backup_apk.ab


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
