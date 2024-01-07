from device import get_devices
from subprocess import TimeoutExpired, run, DEVNULL, STDOUT, PIPE
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
import tkinter

is_macos = "Darwin" in platform.system()


def popen(cmd):
    if is_macos:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                preexec_fn=os.setsid, encoding='utf-8')
    else:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')


def run(cmd_list):
    completedProcess = run(cmd_list, shell=True, stdout=PIPE, stderr=PIPE)
    returncode = completedProcess.returncode
    if returncode == 0:
        ret = completedProcess.stdout.decode('utf-8').strip()
        return ret.split('\n') if ret else ''
    else:
        # sys.stdout.write()
        # log.error(completedProcess.stderr.decode('utf-8').strip())
        return ''


# adb exec-out screencap -p > sc.png
'''
usage: screencap [-hp] [-d display-id] [FILENAME]
   -h: this message
   -p: save the file as a png.
   -d: specify the display id to capture, default 0.
If FILENAME ends with .png it will be saved as a png.
If FILENAME is not given, the results will be printed to stdout.
'''

# adb exec-out screenrecord /sdcard/filename.mp4
'''
Usage: screenrecord [options] <filename>

Android screenrecord v1.2.  Records the device's display to a .mp4 file.

Options:
--size WIDTHxHEIGHT
    Set the video size, e.g. "1280x720".  Default is the device's main
    display resolution (if supported), 1280x720 if not.  For best results,
    use a size supported by the AVC encoder.
--bit-rate RATE
    Set the video bit rate, in bits per second.  Value may be specified as
    bits or megabits, e.g. '4000000' is equivalent to '4M'.  Default 20Mbps.
--bugreport
    Add additional information, such as a timestamp overlay, that is helpful
    in videos captured to illustrate bugs.
--time-limit TIME
    Set the maximum recording time, in seconds.  Default / maximum is 180.
--verbose
    Display interesting information on stdout.
--help
    Show this message.

Recording continues until Ctrl-C is hit or the time limit is reached.
'''

pipes = []
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
d_width = 180
d_height = 400

pool = ThreadPoolExecutor()


def stop_monitor():
    for i in range(0, len(pipes)):
        p = pipes[i]
        # print('index:', i, 'pipe id :', p.pid)
        run('kill %s ' % p.pid if is_macos else 'taskkill /t /f /pid %s ' % p.pid, shell=True, stdout=DEVNULL,
            stderr=DEVNULL)
    pipes.clear()


def start_monitor():
    d_w_x = 0
    d_w_y = 30
    # print('screen size : ', width, height)
    port = 27184
    ds = get_devices()
    ds_size = len(ds)
    colum_size = round(width / d_width)
    # print('colum size:', round(colum_size),'devices size:',ds_size)
    row_index = -1  # 0 0+11 11+11
    for i in range(0, ds_size):
        d = ds[i]
        colum_index = i % colum_size
        if colum_index == 0:
            d_w_x = 0
            row_index = row_index + 1
            d_w_y = d_height * row_index + 30
        else:
            d_w_x = d_width + d_w_x

        # print('colum_index', colum_index, 'd_w_x:', d_w_x, 'd_w_y:', d_w_y)
        if is_macos:
            cmd = 'scrcpy -s %s -m 1024 -p %s' % (
                d, port)
        else:
            cmd = 'scrcpy -s %s -m 1024 -p %s --window-x %s --window-y %s --window-width 180 --window-height 400' % (
                d, port, d_w_x, d_w_y)
        p = popen(cmd)

        port = port - 1
        pipes.append(p)
        time.sleep(1)


if __name__ == "__main__":
    start_monitor()
