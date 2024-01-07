"""
每个模块都是独立没有相互引用，方便抄袭传播这些脚本

Keyword arguments:
argument -- description
Return: return_description
"""

import subprocess
from subprocess import TimeoutExpired, PIPE, DEVNULL, STDOUT
import platform
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor
import signal
import sys
from multiprocessing.connection import Client, Listener, wait, Pipe
from multiprocessing import Queue, Process, Pool, Process, Lock, Value, Array, Manager


def run(cmd_list):
    completedProcess = subprocess.run(
        cmd_list, shell=True, stdout=PIPE, stderr=PIPE)
    returncode = completedProcess.returncode
    if returncode == 0:
        ret = completedProcess.stdout.decode('utf-8').strip()
        return ret.split('\n') if ret else ''
    else:
        # sys.stdout.write()
        # log.error(completedProcess.stderr.decode('utf-8').strip())
        return ''


is_macos = "Darwin" in platform.system()


def popen(cmd):
    if is_macos:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                preexec_fn=os.setsid, encoding='utf-8')
    else:
        return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')


def adb_shell(serial_no, cmd):
    return run('adb -s %s shell %s' % (serial_no, cmd))


def adb_shell_input(serial_no, subcmd, *args, source=''):
    """
    关键字参数不能放在可变参数前面
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
    """
    if len(subcmd) == 0:
        raise BaseException('subcmd must be not empty')
    s = ''
    for i in args:
        s = s + ' ' + str(i)
    adb_shell(serial_no, 'input %s %s %s' % (source, subcmd, s))


__t_pool = ThreadPoolExecutor()


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
    if brand == "HUAWEI" or brand == "HONOR":
        for cmd in cmds:
            run(cmd)
    elif brand == "xiaomi":
        for cmd in cmds:
            run(cmd)
    elif brand == "OPPO" or brand == 'Realme':
        def task(cmds):
            for cmd in cmds:
                run(cmd)

        __t_pool.submit(task, cmds)
        time.sleep(20)
        adb_shell_input(serial_no, 'tap', 799.7405, 1892.8088)
        time.sleep(3)
        # shell(
        #     "adb -s {} shell input tap {}".format(self.serial_no, '360.333 1997.853'))
        time.sleep(30)
        adb_shell_input(serial_no, 'tap', 367.3401, 2076.8875)
    elif brand == "vivo":
        def task(cmds):
            for cmd in cmds:
                run(cmd)

        __t_pool.submit(task, cmds)
        time.sleep(10)
        adb_shell_input(serial_no, 'tap', 360.333, 1997.853)
        time.sleep(3)
        adb_shell_input(serial_no, 'tap', 360.333, 1997.853)
        time.sleep(30)
        adb_shell_input(serial_no, 'tap', 676.6265, 2170.9277)
    print('=====>>>安装完成 %s,%s' % (serial_no, brand))


def running_services(serial_no, packagename):
    """
    adb shell dumpsys activity services [ < packagename > ]
    """
    cmd = 'adb -s %s shell dumpsys activity service %s' % (
        serial_no, packagename)
    run(cmd)


def top_activity(serial_no):
    cmd = 'adb -s %s shell dumpsys activity activities | grep mResumedActivity' % serial_no
    run(cmd)


def open_app(serial_no, act):
    run("adb -s " + serial_no + " shell am start -n {}".format(act))


def __process_list_interal(pipe, serial_no, app_uid):
    try:
        # for line in iter(lambda: pipe.stdout.readline(), ''):
        isFrist = True

        while True:
            line = pipe.stdout.readline()

            if line is None or len(line) == 0:
                print('end' + "=" * 20)
                break
            elif isFrist:
                ret = line.split()
                if ret is not None and len(ret) == 8:
                    uid = ret[0]
                    pid = ret[1]
                    ppid = ret[2]
                    c = ret[3]
                    start_time = ret[4]
                    tty = ret[5]
                    time = ret[6]
                    cmd = ret[7]

                    print(uid + '\t' + pid + '\t' + 'p_oom_score' + '\t' + ppid + '\t' + 'pp_oom_score' + '\t' +
                          c + ' ' + start_time + '   ' + tty + ' ' + time + '\t' + cmd)
                isFrist = False

            elif app_uid in line:
                # -f Full listing (-o USER:12=UID,PID,PPID,C,STIME,TTY,TIME,ARGS=CMD)
                # -l Long listing (-o F,S,UID,PID,PPID,C,PRI,NI,ADDR,SZ,WCHAN,TTY,TIME,CMD)
                ret = line.split()
                if ret is not None and len(ret) == 8:
                    uid = ret[0]
                    pid = ret[1]
                    ppid = ret[2]
                    c = ret[3]
                    start_time = ret[4]
                    tty = ret[5]
                    time = ret[6]
                    cmd = ret[7]

                    adb_cmd = 'adb -s ' + serial_no + ' shell cat /proc/' + pid + '/oom_score'
                    p_oom_score = os.popen(adb_cmd).read().strip()
                    adb_cmd = 'adb -s ' + serial_no + ' shell cat /proc/' + ppid + '/oom_score'
                    pp_oom_score = os.popen(adb_cmd).read().strip()
                    print(uid + '\t' + pid + '\t' + p_oom_score + '\t\t' + ppid + '\t' + pp_oom_score + '\t\t' +
                          c + ' ' + start_time + ' ' + tty + ' ' + time + '\t' + cmd)

    except KeyboardInterrupt as e:
        os.killpg(pipe.pid, signal.SIGINT)
    except TimeoutExpired as e:
        os.killpg(pipe.pid, signal.SIGINT)


def process_list(serial_no, pkg_name):
    # adb  shell ps -ef |findstr "com.hawksjamesf"
    if is_macos:
        uid = os.popen('adb  -s ' + serial_no + ' shell dumpsys package ' +
                       pkg_name + ' | grep userId= ').read().strip()
        if not uid: return ''
        uid = 'u0_a' + uid.split('=')[1][-3:]
    else:
        if not uid: return ''
        uid = os.popen('adb  -s ' + serial_no + ' shell dumpsys package ' +
                       pkg_name + '| findstr userId= ').read().strip()
        uid = 'u0_a' + uid.split('=')[1][-3:]
    with popen("adb -s " + serial_no + " shell ps -ef") as pipe:
        __process_list_interal(pipe, serial_no, uid)


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

if __name__ == "__main__":
    # while True:
    process_list('emulator-5554 ', 'com.sankuai.meituan')
    process_list('emulator-5554 ', 'com.hawksjamesf.spacecraft.debug')
    process_list('emulator-5554 ', 'com.jamesfchen.b')
    # time.sleep(1)
