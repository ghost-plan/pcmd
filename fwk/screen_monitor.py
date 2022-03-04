

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
def __cmd_list(cmd, fn=None):
    print('[ cmd ] ', cmd, end='\n')
    if fn is None:
        run(cmd, shell=True)
    else:
        with compat.popen(cmd) as pipe:
            try:
                res = pipe.communicate()[0]
                fn(res)
            except KeyboardInterrupt as e:
                os.killpg(pipe.pid, signal.SIGINT)
            except TimeoutExpired as e:
                os.killpg(pipe.pid, signal.SIGINT)


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
