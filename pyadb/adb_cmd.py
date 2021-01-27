import time
import re
import sys
import os
import functools
from subprocess import TimeoutExpired, PIPE, DEVNULL, STDOUT, PIPE, run


def __cmd_list(cmd_list):
    completedProcess = run(cmd_list, shell=True, stdout=PIPE, stderr=PIPE)
    returncode = completedProcess.returncode
    if returncode == 0:
        o = completedProcess.stdout.decode('utf-8').strip()
        return (o.split('\n') if o else o, returncode)
    else:
        return (completedProcess.stderr.decode('utf-8').strip(), returncode)


def adb_shell_cmd(serial_no, cmd_list):
    return __cmd_list('adb -s %s shell %s' % (serial_no, cmd_list))


def adb_push_cmd(serial_no, src, dest):
    return __cmd_list('adb -s %s push %s %s' % (serial_no, src, dest))


def adb_pull_cmd(serial_no, src, dest):
    return __cmd_list('adb -s %s pull %s %s' % (serial_no, src, dest))


def adb_input_cmd(serial_no, source='', subcmd='', *args):
    '''
    The sources are:
        mouse
        keyboard
        joystick
        touchnavigation
        touchpad
        trackball
        stylus
        dpad
        gesture
        touchscreen
        gamepad
    '''
    if len(subcmd) == 0:
        raise BaseException('subcmd must be not empty')
    s = ''
    for i in args:
        s = s+' '+str(i)
    cmd = 'adb -s %s shell input %s %s %s' % (serial_no, source, subcmd, s)
    __cmd_list(cmd)


if __name__ == '__main__':
    pass
