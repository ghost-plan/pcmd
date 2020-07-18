from enum import Enum, unique
import time
import functools
import os
import re
import sys
from subprocess import TimeoutExpired, PIPE, DEVNULL, Popen
import signal


def adb_shell_cmd(serial_no, cmd_list, silent=False):
    if not silent:
        with os.popen('adb -s %s shell %s' % (serial_no, cmd_list)) as p:
            return p.readlines()
    else:
        with Popen('adb -s %s shell %s' % (serial_no, cmd_list), stdout=DEVNULL, stderr=DEVNULL, shell=True,
                   preexec_fn=os.setsid, encoding='utf-8') as pipe:
            try:
                res = pipe.communicate()[0]
                return res
            except TimeoutExpired as e:
                os.killpg(pipe.pid, signal.SIGINT)
                out_bytes = pipe.communicate()[0]


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


def check_device(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        for arg in args:
            if arg in get_devices():
                return func(*args, **kw)
            else:
                sys.stdout.write('device not found')
                sys.exit(1)
    return wrapper


# def check_device_with_arg(arg):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kw):
#             print("check_device_with_arg")
#             # if device in devices:
#             #     return True
#             # else:
#             #     return False
#             return func(*args, **kw)

#         return wrapper
#     return decorator

@check_device
def get_model(serial_no):
    ret = adb_shell_cmd(serial_no, 'getprop ro.product.model')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
# ro.product.brand
def get_brand(serial_no):
    ret = adb_shell_cmd(serial_no, 'getprop ro.product.brand')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
# ro.product.name
def get_name(serial_no):
    ret = adb_shell_cmd(serial_no, 'getprop ro.product.name')
    return ret[0].strip() if ret and len(ret) > 0 else ''

# adb shell wm size
# Physical size: 1080x1920
# Override size: 480x1024


@check_device
def get_wm_size(serial_no, is_override=False):
    ret = adb_shell_cmd(serial_no, 'wm size')
    if ret is None or len(ret) == 0:
        return '', ''

    line = 1 if is_override else 0
    ret = ret[line].split(':')[1].strip().split('x')
    screen_width = int(ret[0].strip())
    screen_height = int(ret[1].strip())
    return screen_width, screen_height


# adb shell wm density
# Physical density: 480
# Override density: 160
@check_device
def get_wm_density(serial_no, is_override=False):
    ret = adb_shell_cmd(serial_no, 'wm density')
    line = 1 if is_override else 0
    return int(ret[line].split(':')[1].strip())


# adb shell dumpsys window displays
@check_device
def get_wm_displays(serial_no):
    ret = adb_shell_cmd(serial_no, 'dumpsys window displays')
    # TODO:parser window displas


@check_device
# adb shell settings get secure android_id
def get_android_id(serial_no):
    ret = adb_shell_cmd(serial_no, 'settings get secure android_id')
    return ret[0].strip()


def compare(first: int, sec: int):
    if first > sec:
        return 1
    elif first < sec:
        return -1
    else:
        return 0


def compare_list(i, first, sec):
    a = first[i] if len(first) > i else 0
    aa = sec[i] if len(sec) > i else 0
    if i == 3:
        return 0
    a = int(a)
    aa = int(aa)
    ret = compare(a, aa)
    # print(i, a, aa)
    if ret == 0:
        i = i+1
        return compare_list(i, first, sec)
    else:
        return ret


def compare_version(first_ver, sec_ver):
    first_vers = first_ver.split('.')
    sec_vers = sec_ver.split('.')
    if len(first_vers) < 1 or len(sec_vers) < 1:
        raise BaseException("版本号不符合要求,应为xxx.xxx.xxx")
    return compare_list(0, first_vers, sec_vers)


def get_android_version(serial_no):
    ret = adb_shell_cmd(
        serial_no, 'getprop ro.build.version.release')
    return ret[0].strip()


@check_device
# adb shell dumpsys iphonesubinfo
def get_imei(serial_no):
    first = get_android_version(serial_no)
    sec = '4.4.3'
    if compare_version(first, sec) > 0:
        ret = adb_shell_cmd(serial_no, 'service call iphonesubinfo 1')
        imei = ''
        for line in ret[1:]:
            imei += line.split("'")[1].replace('.', "").strip()
        return imei
    else:
        ret = adb_shell_cmd(serial_no, 'dumpsys iphonesubinfo')
        # ret = ['Phone Subscriber Info: Phone Type = GSM Device ID = 860955027785041']
        imei = ret[0].split('=')[-1].strip()
        return imei


@check_device
def get_ip_and_mac(serial_no):
    ret = adb_shell_cmd(serial_no, 'ifconfig | grep Mask', silent=True)
    if ret is None or len(ret) == 0:
        ret = adb_shell_cmd(serial_no, 'ifconfig  wlan0', silent=True)
        if ret is None or len(ret) == 0:
            ret = adb_shell_cmd(serial_no, 'netcfg')
            for e in ret:
                r = e.split()
                if '0.0.0.0/0' not in r and '127.0.0.1/8' not in r:
                    return r[-2], r[-1]
                # if 'wlan0' in e:
                # else
    # print('ret', ret)


@check_device
# ro.product.board
def get_board(serial_no):
    ret = adb_shell_cmd(serial_no, 'getprop ro.product.board')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
# ro.product.abilist
def get_abilist(serial_no):
    ret = adb_shell_cmd(serial_no, 'getprop ro.product.cpu.abilist')
    if len(ret) == 0:
        # adb shell cat /system/build.prop | grep ro.product.cpu.abi
        ret = adb_shell_cmd(
            serial_no, 'cat /system/build.prop | grep ro.product.cpu.abi')
        ret = ['ro.product.cpu.abi = armeabi-v7a',
               'ro.product.cpu.abi2 = armeabi']
        abilist = []
        for e in ret:
            abilist.append(e.split('=')[1].strip())
        print(abilist)
        return abilist

    return ret[0].strip().split(',') if ret and len(ret) > 0 else ''


@ check_device
# adb shell cat / proc/cpuinfo
def get_cpu_core_size(serial_no):
    ret = adb_shell_cmd(serial_no, 'cat /proc/cpuinfo')
    for i in range(len(ret)-1, -1, -1):
        line = ret[i]
        if re.match("^processor*", line):
            return int(line.split(':')[1])+1


@unique
class Unit(Enum):
    B = 1
    K = 1024
    M = 1024*K
    G = 1024*M


@ check_device
# dalvik.vm.heapsize,unit m
def get_heap_size(serial_no, unit=Unit.M):
    ret = adb_shell_cmd(serial_no, 'getprop dalvik.vm.heapsize')
    if len(ret) == 0:
        return ''
    ret = ret[0].strip().split('m')[0]
    if unit == Unit.B:
        return ret*Unit.M
    elif unit == Unit.K:
        return ret*Unit.K
    elif unit == Unit.M:
        return ret
    elif unit == Unit.G:
        return ret/1024


@ check_device
# adb shell cat / proc/meminfo
def get_men_info(serial_no):
    # MemTotal 就是设备的总内存，MemFree 是当前空闲内存
    ret = adb_shell_cmd(serial_no, 'cat /proc/meminfo')


@ check_device
# adb shell dumpsys battery
def get_battery_info(serial_no):
    pass


def main():
    for d in get_devices():
        print('='*50)
        print('model:"', get_model(d))
        print('brand:"', get_brand(d))
        print('name:"', get_name(d))
        print('wm size:', get_wm_size(d))
        print('wm density:', get_wm_density(d))
        print('android version:', get_android_version(d))
        print('imei:', get_imei(d))
        print('ip/mac:', get_ip_and_mac(d))
        print('board:"', get_board(d))
        print('abilist:"', get_abilist(d))
        print('cpu core size:', get_cpu_core_size(d))
        print('heap size/m:"', get_heap_size(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))
        # print(get_ip(d))


if __name__ == '__main__':
    main()
