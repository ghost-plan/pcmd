from enum import Enum, unique
import time
from subprocess import TimeoutExpired, PIPE, DEVNULL, STDOUT
import subprocess
import functools, os, sys, re, time


def run(cmd_list):
    completedProcess = subprocess.run(cmd_list, shell=True, stdout=PIPE, stderr=PIPE)
    returncode = completedProcess.returncode
    if returncode == 0:
        ret = completedProcess.stdout.decode('utf-8').strip()
        return ret.split('\n') if ret else ''
    else:
        # sys.stdout.write()
        # log.error(completedProcess.stderr.decode('utf-8').strip())
        return ''


def adb_shell(serial_no, cmd):
    return run('adb -s %s shell %s' % (serial_no, cmd))


def get_devices():
    with os.popen("adb devices") as p:
        ret = p.readlines()
        if ret is None or len(ret) == 0:
            return []
        ds = []
        for line in ret[1:]:
            if re.match(".*device$", line):
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
    ret = adb_shell(serial_no, 'getprop ro.product.model')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
def get_brand(serial_no):
    # ro.product.brand
    ret = adb_shell(serial_no, 'getprop ro.product.brand')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
def get_name(serial_no):
    # ro.product.name
    ret = adb_shell(serial_no, 'getprop ro.product.name')
    return ret[0].strip() if ret and len(ret) > 0 else ''


@check_device
def get_wm_size(serial_no, is_override=False):
    """
    # adb shell wm size
    # Physical size: 1080x1920
    # Override size: 480x1024
    """
    ret = adb_shell(serial_no, 'wm size')
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
    ret = adb_shell(serial_no, 'wm density')
    line = 1 if is_override else 0
    return int(ret[line].split(':')[1].strip())


@check_device
def get_wm_displays(serial_no):
    # adb shell dumpsys window displays
    ret = adb_shell(serial_no, 'dumpsys window displays')
    # TODO:parser window displas


@check_device
def get_android_id(serial_no):
    # adb shell settings get secure android_id
    ret = adb_shell(serial_no, 'settings get secure android_id')
    return ret[0].strip() if ret and len(ret) > 0 else ''


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
        i = i + 1
        return compare_list(i, first, sec)
    else:
        return ret


def compare_version(first_ver, sec_ver):
    first_vers = first_ver.split('.')
    sec_vers = sec_ver.split('.')
    if len(first_vers) < 1 or len(sec_vers) < 1:
        raise RuntimeError("版本号不符合要求,应为xxx.xxx.xxx")
    return compare_list(0, first_vers, sec_vers)


def get_android_version(serial_no):
    ret = adb_shell(
        serial_no, 'getprop ro.build.version.release')
    return ret[0].strip()


def __get_number(serial_no, ret):
    imei = ''
    for line in ret[1:]:
        if line is None or len(line) == 0:
            continue
        r = line.split("'")[1].replace('.', "").strip()
        imei += r
    return imei


def __is_imei(value):
    if value is None or len(value) != 15:
        return False
    return True if value.startswith('8') else False


@check_device
def get_imeis(serial_no):
    # adb shell dumpsys iphonesubinfo
    first = get_android_version(serial_no)
    sec = '4.4.3'
    if compare_version(first, sec) > 0:
        imeis = set()
        b = get_brand(serial_no)
        if b == 'HUAWEI' or b == 'HONOR' or b == 'Xiaomi':
            for i in range(0, 20):
                ret = adb_shell(
                    serial_no, 'service call iphonesubinfo %s' % i)
                n = __get_number(serial_no, ret)
                if __is_imei(n):
                    imeis.add(n)

        elif b == 'Realme' or b == 'OPPO' or b == 'vivo':
            for i in range(1, 3):
                ret = adb_shell(
                    serial_no, 'service call iphonesubinfo 3 i32 %s' % i)
                n = __get_number(serial_no, ret)
                if __is_imei(n):
                    imeis.add(n)
        return imeis
    else:
        ret = adb_shell(serial_no, 'dumpsys iphonesubinfo')
        # ret = ['Phone Subscriber Info: Phone Type = GSM Device ID = 860955027785041']
        imei = ret[0].split('=')[-1].strip()
        return imei


@check_device
def get_ip_and_mac(serial_no):
    ret = adb_shell(serial_no, 'ifconfig | grep Mask')
    if ret is None or len(ret) == 0:
        ret = adb_shell(serial_no, 'ifconfig  wlan0')
        if ret is None or len(ret) == 0:
            ret = adb_shell(serial_no, 'netcfg')
            for e in ret:
                r = e.split()
                if '0.0.0.0/0' not in r and '127.0.0.1/8' not in r:
                    if '0x' in r[-1]:
                        return r[-2], ''
                    return r[-2], r[-1]

    else:
        ip = ret[0].strip().split(':')[1].strip()[0]
        s: str = ret[0].strip()
        start = s.index('inet addr:') + len('inet addr:')
        end = start + 11
        ip = s[start:end]
        return ip, ''


@check_device
# ro.product.board
def get_board(serial_no):
    ret = adb_shell(serial_no, 'getprop ro.product.board')
    return ret[0].strip() if ret and len(ret) > 0 else ''


# ========================================cpu start====================================================================
'''
下面两个指标体现cpu性能
// 获取 CPU 核心数
cat /sys/devices/system/cpu/possible  

// 获取某个 CPU 的频率
cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq

下面指标体现cpu使用率（反应了cpu在某个进程中的使用情况）

proc/self/stat:
  utime:       用户时间，反应用户代码执行的耗时  
  stime:       系统时间，反应系统调用执行的耗时
  majorFaults：需要硬盘拷贝的缺页次数
  minorFaults：无需硬盘拷贝的缺页次数

下面指标体现cpu饱和度（反应了线程排队等待cpu情况）

proc/self/sched:
  nr_voluntary_switches：     
  主动上下文切换次数，因为线程无法获取所需资源导致上下文切换，最普遍的是IO。    
  nr_involuntary_switches：   
  被动上下文切换次数，线程被系统强制调度导致上下文切换，例如大量线程在抢占CPU。
  se.statistics.iowait_count：IO 等待的次数
  se.statistics.iowait_sum：  IO 等待的时间
'''


@check_device
# ro.product.abilist
def get_abilist(serial_no):
    ret = adb_shell(serial_no, 'getprop ro.product.cpu.abilist')
    if len(ret) == 0:
        # adb shell cat /system/build.prop | grep ro.product.cpu.abi
        ret = adb_shell(
            serial_no, 'cat /system/build.prop | grep ro.product.cpu.abi')
        ret = ['ro.product.cpu.abi = armeabi-v7a',
               'ro.product.cpu.abi2 = armeabi']
        abilist = []
        for e in ret:
            abilist.append(e.split('=')[1].strip())
        print(abilist)
        return abilist

    return ret[0].strip().split(',') if ret and len(ret) > 0 else ''


@check_device
def get_cpu_core_size(serial_no):
    """
    ['Processor\t: AArch64 Processor rev 4 (aarch64)\r', 'processor\t: 0\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd03\r', 'CPU revision\t: 4\r', '\r', 'processor\t: 1\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd03\r', 'CPU revision\t: 4\r', '\r', 'processor\t: 2\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd03\r', 'CPU revision\t: 4\r', '\r', 'processor\t: 3\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd03\r', 'CPU revision\t: 4\r', '\r', 'processor\t: 4\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd09\r', 'CPU revision\t: 2\r', '\r', 'processor\t: 5\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd09\r', 'CPU revision\t: 2\r', '\r', 'processor\t: 6\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t:
0x0\r', 'CPU part\t: 0xd09\r', 'CPU revision\t: 2\r', '\r', 'processor\t: 7\r', 'BogoMIPS\t: 3.84\r', 'Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid\r', 'CPU implementer\t: 0x41\r', 'CPU architecture: 8\r', 'CPU variant\t: 0x0\r', 'CPU part\t: 0xd09\r', 'CPU revision\t: 2\r', '\r', 'Hardware\t: Hisilicon Kirin710']
    """
    # adb shell cat / proc/cpuinfo
    ret = adb_shell(serial_no, 'cat /proc/cpuinfo')
    for i in range(len(ret) - 1, -1, -1):
        line = ret[i]
        if re.match("^processor*", line):
            return int(line.split(':')[1]) + 1

# ========================================cpu end=======================================================================

# ========================================process start=================================================================
    '''
    /proc/[pid]/stat             // 进程CPU使用情况
    /proc/[pid]/task/[tid]/stat  // 进程下面各个线程的CPU使用情况
    /proc/[pid]/sched            // 进程CPU调度相关
    /proc/loadavg                // 系统平均负载，uptime命令对应文件
    '''


# ========================================process end==================================================================
@unique
class Unit(Enum):
    B = 1
    K = 1024
    M = 1024 * K
    G = 1024 * M


@check_device
def get_heap_size(serial_no, unit=Unit.M):
    # dalvik.vm.heapsize,unit m
    ret = adb_shell(serial_no, 'getprop dalvik.vm.heapsize')
    if len(ret) == 0:
        return ''
    ret = ret[0].strip().split('m')[0]
    if unit == Unit.B:
        return ret * Unit.M
    elif unit == Unit.K:
        return ret * Unit.K
    elif unit == Unit.M:
        return ret
    elif unit == Unit.G:
        return ret / 1024


@check_device
def get_mem_info(serial_no):
    """
    ['MemTotal:        3768292 kB\r', 'MemFree:           82008 kB\r', 'MemAvailable:    1763668 kB\r', 'Buffers:            4780 kB\r', 'Cached:          1671212 kB\r', 'SwapCached:       136492 kB\r', 'Active:
        1701080 kB\r', 'Inactive:        1148344 kB\r', 'Active(anon):     818020 kB\r', 'Inactive(anon):   365260 kB\r', 'Active(file):     883060 kB\r', 'Inactive(file):   783084 kB\r', 'Unevictable:
2296 kB\r', 'Mlocked:            2296 kB\r', 'SwapTotal:       2293756 kB\r', 'SwapFree:        1703164 kB\r', 'Dirty:               212 kB\r', 'Writeback:             0 kB\r', 'AnonPages:       1163972 kB\r', 'Mapped:           404768 kB\r', 'Shmem:              9744 kB\r', 'Slab:             258684 kB\r', 'SReclaimable:      91428 kB\r', 'SUnreclaim:       167256 kB\r', 'KernelStack:       53440 kB\r', 'PageTables:        78428 kB\r', 'NFS_Unstable:          0 kB\r', 'Bounce:                0 kB\r', 'WritebackTmp:          0 kB\r', 'CommitLimit:     4177900 kB\r', 'Committed_AS:   93899432 kB\r', 'VmallocTotal:   263061440 kB\r', 'VmallocUsed:           0 kB\r', 'VmallocChunk:          0 kB\r', 'CmaTotal:         262144 kB\r', 'CmaFree:             192 kB\r', 'IonTotalCache:         0 kB\r', 'IonTotalUsed:      74420 kB\r', 'RsvTotalUsed:     276484 kB']
    """
    # adb shell cat / proc/meminfo
    # MemTotal 就是设备的总内存，MemFree 是当前空闲内存
    ret = adb_shell(serial_no, 'cat /proc/meminfo')


@check_device
def get_battery_info(serial_no):
    # adb shell dumpsys battery
    ret = adb_shell(serial_no, 'dumpsys battery')
    level = ''
    scale = ''

    for line in ret:
        if 'level' in line:
            level = line.split(':')[1].strip()
        elif 'scale' in line:
            scale = line.split(':')[1].strip()
    return '%s/%s' % (level, scale)


@check_device
def get_iccid(serial_no):
    ret = adb_shell(
        serial_no, 'service call iphonesubinfo %s' % 11)
    n = __get_number(serial_no, ret)
    return n


@check_device
def get_imsi(serial_no):
    # adb shell service call iphonesubinfo 7 TelephonyManager.getSubscriberId()
    i = 7
    ret = adb_shell(
        serial_no, 'service call iphonesubinfo %s' % i)
    n = __get_number(serial_no, ret)
    return n


@check_device
def switch_airplane(s):
    adb_shell(s, "am force-stop com.android.settings")
    time.sleep(2)
    adb_shell(s, "am start com.android.settings")
    print('switch_airplane: am start com.android.settings')
    adb_shell(s, "input tap 10 30")
    time.sleep(2)
    brand = get_brand(s)
    model = get_model(s)
    version = get_android_version(s)
    print('switch_airplane:', brand, model, version)
    if brand == "HUAWEI" or brand == "HONOR":
        if model == 'JAT-AL00':
            time.sleep(2)
            adb_shell(s, " input tap 408.0 429.0")
            time.sleep(5)
            adb_shell(s, " input tap 627.0 189.0")
            time.sleep(20)
            adb_shell(s, " input tap 627.0 189.0")
            time.sleep(10)
        else:
            if int(version) == 10:
                time.sleep(2)
                adb_shell(
                    s, " input tap 396.3 1420.5")
                time.sleep(5)
                adb_shell(s, " input tap 944.8 318.1")
                time.sleep(20)
                adb_shell(s, " input tap 952.8 312.1")
                time.sleep(10)
            else:
                time.sleep(2)
                adb_shell(s, " input tap 1000 600")
                time.sleep(2)
                time.sleep(5)
                adb_shell(s, " input tap 1000 300")
                time.sleep(20)
                adb_shell(s, " input tap 1000 300")
                time.sleep(10)
    if brand == "xiaomi":
        if s == 'ee58c490':
            time.sleep(2)
            adb_shell(s, " input tap 643.5 1464.6")
            time.sleep(5)
            adb_shell(s, " input tap 952.8 1250.5")
            time.sleep(20)
            adb_shell(s, " input tap 952.8 1250.5")
            time.sleep(10)
        else:
            time.sleep(2)
            adb_shell(s, " input tap 1000 1520")
            time.sleep(5)
            adb_shell(s, " input tap 1000 300")
            time.sleep(20)
            adb_shell(s, " input tap 1000 300")
            time.sleep(10)

    if brand == "OPPO" or brand == 'Realme':
        if model == "PCLM50":
            time.sleep(5)
            adb_shell(s, " input tap 1000 900")
            time.sleep(20)
            adb_shell(s, " input tap 1000 900")
            time.sleep(10)
        else:
            if int(version) == 10:
                time.sleep(5)
                adb_shell(s, " input tap 861.79 955.40829")
                time.sleep(20)
                adb_shell(s, " input tap 861.79 955.40829")
                time.sleep(10)
            else:
                time.sleep(5)
                adb_shell(s, " input tap 1000 600")
                time.sleep(20)
                adb_shell(s, " input tap 1000 600")
                time.sleep(10)

    if brand == "vivo":
        if model == "V1965A":
            time.sleep(5)
            adb_shell(s, " input tap 1000 1200")
            time.sleep(5)
            adb_shell(s, " input tap 950 400")
            time.sleep(20)
            adb_shell(s, " input tap 950 400")
            time.sleep(10)
        else:
            if int(version) == 10:
                time.sleep(5)
                adb_shell(s, " input tap 401.3 1543.6")
                time.sleep(5)
                adb_shell(s, " input tap 980.9 387.16")
                time.sleep(20)
                adb_shell(s, " input tap 980.9 387.16")
                time.sleep(10)
            else:
                time.sleep(5)
                adb_shell(s, " input tap 1000 1200")
                time.sleep(20)
                adb_shell(s, " input tap 1000 1200")
                time.sleep(10)


@check_device
def dimiss_dialog(serial_no, text, i):
    if '传输文件' in text and '仅充电' in text:
        start = time.time()
        brand = get_brand(serial_no)
        name = get_name(serial_no)
        if 'OPPO' in brand or 'Realme' in brand:
            run("adb -s %s shell input tap 815.755  1793.7665" %
                serial_no, shell=True, stdout=DEVNULL)
            time.sleep(2)
        print('%d %s：关闭传输文件弹窗,耗时：%dms' % (i, serial_no, time.time() - start))
    if '软件更新' in text:
        start = time.time()
        brand = get_brand(serial_no)
        name = get_name(serial_no)
        if 'HONOR' in brand and 'JAT-AL00' in name:
            run("adb -s %s shell input tap 147.0  1392.0" %
                serial_no, shell=True, stdout=DEVNULL)
            time.sleep(2)
        else:
            run("adb -s %s shell input tap 168.15  2074.886" %
                serial_no, shell=True, stdout=DEVNULL)
            time.sleep(2)
            run("adb -s %s shell input tap 256.237  2074.886" %
                serial_no, shell=True, stdout=DEVNULL)
            time.sleep(2)
        print('%d %s：关闭需要系统更新弹窗,耗时：%dms' % (i, serial_no, time.time() - start))
    else:
        print('%d %s：不用关闭系统更新弹窗' % (i, serial_no))


def main():
    for d in get_devices():
        print('=' * 50)
        print('serial_no:', d)
        print('brand:', get_brand(d))
        print('model:', get_model(d))
        print('name:', get_name(d))
        print('board:', get_board(d))
        print('wm size:', get_wm_size(d))
        print('wm density:', get_wm_density(d))
        print('android version:', get_android_version(d))
        print('heap size/m:', get_heap_size(d))
        print('cpu core size:', get_cpu_core_size(d))
        print('abilist:', get_abilist(d))
        print('memory:', get_mem_info(d))

        print('android id:', get_android_id(d))
        print('imeis:', get_imeis(d))
        print('ip/mac:', get_ip_and_mac(d))
        print('battery:', get_battery_info(d))
        print('iccid:', get_iccid(d))
        print('imsi:', get_imsi(d))
        # switch_airplane(d)


if __name__ == '__main__':
    main()
