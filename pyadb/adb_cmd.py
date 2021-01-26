from subprocess import TimeoutExpired, PIPE, DEVNULL, Popen, STDOUT, PIPE, run, TimeoutExpired
import functools
import os
import sys
import re
import time
def _cmd(serial_no, cmd_list):
    completedProcess = run(cmd_list,shell=True, stdout=PIPE, stderr=PIPE)
    returncode = completedProcess.returncode
    if returncode == 0:
        o = completedProcess.stdout.decode('utf-8').strip()
        return (o.split('\n') if o else o, returncode)
    else:
        return (completedProcess.stderr.decode('utf-8').strip(), returncode)
def adb_shell_cmd(serial_no, cmd_list):
    return _cmd(serial_no, 'adb -s %s shell %s' % (serial_no, cmd_list))

def adb_push_cmd(serial_no, cmd_list):
    return _cmd(serial_no, 'adb -s %s push %s' % (serial_no, cmd_list))


def get_devices():
    with os.popen("adb devices") as p:
        ret = p.readlines()
        if ret is None or len(ret) == 0:
            return []
        ds = []
        for line in ret[1:]:
            if (re.match(".*device$", line)):
                ds.append(line.split("\t")[0])
        return ds
if __name__ =='__main__':
    for d in get_devices():
        ret = adb_shell_cmd(d, 'settings get secure android_id')
        print(ret)
