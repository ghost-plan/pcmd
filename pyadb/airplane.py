import time
from subprocess import run, Popen, PIPE, TimeoutExpired
import signal
import os


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


def switch_airplane(s):
    __cmd_list("adb -s " + s + "  shell am force-stop com.android.settings")

    time.sleep(2)
    __cmd_list("adb -s " + s + "  shell am start com.android.settings")
    __cmd_list("adb -s " + s + " shell input tap 10 30")
    time.sleep(2)
    brand = os.popen(
        "adb -s " + s + "  shell getprop ro.product.brand").readlines()[0].strip()
    if brand == "HUAWEI":
        time.sleep(2)
        __cmd_list("adb -s " + s + " shell input tap 1000 600")
        time.sleep(2)
        time.sleep(5)
        __cmd_list("adb -s " + s + " shell input tap 1000 300")
        time.sleep(20)
        __cmd_list("adb -s " + s + " shell input tap 1000 300")
        time.sleep(10)
    if brand == "xiaomi":
        time.sleep(2)
        __cmd_list("adb -s " + s + " shell input tap 1000 1500")
        time.sleep(5)
        __cmd_list("adb -s " + s + " shell input tap 1000 300")
        time.sleep(20)
        __cmd_list("adb -s " + s + " shell input tap 1000 300")
        time.sleep(10)

    if brand == "OPPO":
        time.sleep(5)
        __cmd_list("adb -s " + s + " shell input tap 1000 600")
        time.sleep(20)
        __cmd_list("adb -s " + s + " shell input tap 1000 600")
        time.sleep(10)

    if brand == "vivo":
        time.sleep(5)
        __cmd_list("adb -s " + s + " shell input tap 1000 1200")
        time.sleep(20)
        __cmd_list("adb -s " + s + " shell input tap 1000 1200")
        time.sleep(10)
