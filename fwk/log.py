"""
pc控制台与手机控制台日志

Keyword arguments:
argument -- description
Return: return_description
"""

from subprocess import PIPE, TimeoutExpired
import subprocess
import platform
import os, signal
from enum import Enum, unique
import sys

ANSI_RED = "\u001B[31m"
ANSI_YELLOW = "\u001B[33m"
ANSI_GREEN = "\u001B[32m"
ANSI_BLUE = "\u001B[34m"
ANSI_RED_BACKGROUND = "\u001B[41m"
ANSI_GREEN_BACKGROUND = "\u001B[42m"
ANSI_YELLOW_BACKGROUND = "\u001B[43m"
ANSI_BLUE_BACKGROUND = "\u001B[44m"
ANSI_RESET = "\u001B[0m"
is_macos = "Darwin" in platform.system()


def popen(cmd):
    if is_macos:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                preexec_fn=os.setsid, encoding='utf-8')
    else:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')


def error(*message):
    s = ''
    for i in message:
        s = s + str(i)
    print(ANSI_RED + s + ANSI_RESET)


def warn(*message):
    s = ''
    for i in message:
        s = s + str(i)
    print(ANSI_YELLOW + s + ANSI_RESET)


def info(*message):
    s = ''
    for i in message:
        s = s + str(i)
    print(ANSI_GREEN + s + ANSI_RESET)


def debug(*message):
    s = ''
    for i in message:
        s = s + str(i)
    print(ANSI_BLUE + s + ANSI_RESET)


def verbose(*message):
    s = ''
    for i in message:
        s = s + str(i)
    print(s)


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
        s = s + str(i)
    print(bar[pos % len(bar)] + ' ' + s + '\r')


# log.Format.BRIEF.value
# log.Format.BRIEF.name
@unique
class Format(Enum):
    NONE = 0
    BRIEF = 1  # <priority>/<tag>(<pid>): <message>
    PROCESS = 2  # <priority>(<pid>) <message>
    TAG = 3  # <priority>/<tag>: <message>
    RAW = 4  # <message>
    TIME = 5  # <datetime> <priority>/<tag>(<pid>): <message>
    THREADTIME = 6  # <datetime> <pid> <tid> <priority> <tag>: <message>
    LONG = 7  # [ <datetime> <pid>:<tid> <priority>/<tag> ]
    # <message>


__pros = {"V", "D", "I", "W", "E"}


def __extra_priority(line, format):
    if line is None or len(line) == 0: return None
    if format == Format.NONE:
        ss = line.split()
        return ss[4].strip() if len(ss) > 5 and ss[4].strip() in __pros else None
    elif format == Format.BRIEF:
        ss = line.split("/")
        return ss[0].strip() if len(ss) > 0 and ss[0].strip() in __pros else None
    elif format == Format.PROCESS:
        ss = line.split("(")
        return ss[0].strip() if len(ss) > 0 and ss[0].strip() in __pros else None
    elif format == Format.TAG:
        ss = line.split("/")
        return ss[0].strip() if len(ss) > 0 and ss[0].strip() in __pros else None
    elif format == Format.RAW:
        return None
    elif format == Format.TIME:
        ss = line.split()
        return ss[2].split("/")[0].strip() if len(ss) > 3 and ss[2].split("/")[0].strip() in __pros else None
    elif format == Format.THREADTIME:
        ss = line.split()
        return ss[4].strip() if len(ss) > 5 and ss[4].strip() in __pros else None
    elif format == Format.LONG:
        return None


def capture_log(serial_no, tags, format=Format.NONE):
    if tags and len(tags) > 0:
        cmd = 'adb -s %s  shell logcat *:S' % (serial_no)
        for t in tags:
            cmd = cmd + ' %s:V ' % t.strip()
    else:
        cmd = 'adb -s %s  shell logcat' % (serial_no)
    if format != Format.NONE:
        cmd = cmd + ' -v %s' % format.name.lower()
    with popen(cmd) as pipe:
        try:
            # for line in iter(lambda: pipe.stdout.readline(), ''):
            while True:
                line = pipe.stdout.readline()
                prior = __extra_priority(line, format)
                if "V" == prior:
                    verbose(line)
                    pass
                elif "D" == prior:
                    debug(line)
                    pass
                elif "I" == prior:
                    info(line)
                    pass
                elif "W" == prior:
                    warn(line)
                    pass
                elif "E" == prior:
                    error(line)
                    pass
                else:
                    print(line)
        except KeyboardInterrupt as e:
            os.killpg(pipe.pid, signal.SIGINT)
        except TimeoutExpired as e:
            os.killpg(pipe.pid, signal.SIGINT)
