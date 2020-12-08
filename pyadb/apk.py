

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
from pyadb.utils import is_macos

__t_pool = ThreadPoolExecutor()


def __cmd_list(cmd, fn=None):
    print('[ cmd ] ', cmd, end='\n')
    if fn is None:
        run(cmd, shell=True)
    else:
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                   preexec_fn=os.setsid, encoding='utf-8') as pipe:
            try:
                res = pipe.communicate()[0]
                fn(res)
            except KeyboardInterrupt as e:
                os.killpg(pipe.pid, signal.SIGINT)
            except TimeoutExpired as e:
                os.killpg(pipe.pid, signal.SIGINT)


def am_cmd(serial_no):
    pass


def pm_cmd(serial_no):
    ''' adb shell pm list packages [-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]'''
    pass


def top_activity(serial_no):
    cmd = 'adb -s %s shell dumpsys activity activities | grep mResumedActivity' % serial_no
    __cmd_list(cmd)


def running_services(serial_no, packagename):
    '''adb shell dumpsys activity services [ < packagename > ]'''
    cmd = 'adb -s %s shell dumpsys activity service %s' % (
        serial_no, packagename)
    __cmd_list(cmd)


def open_app(serial_no, act):
    __cmd_list("adb -s "+serial_no + " shell am start -n {}".format(act))
def process_list(serial_no,pkg_name):
    # adb  shell ps -ef |findstr "com.hawksjamesf" 
    if is_macos():
        _cmd_list("adb -s "+serial_no + " shell ps -ef |grep '{}'".format(pkg_name))
    else:
        _cmd_list("adb -s "+serial_no + " shell ps -ef |findstr '{}'".format(pkg_name))
def oomadj_list(serial_no,pid):
    #proc/oom_adj
    if is_macos():
        pass
        
