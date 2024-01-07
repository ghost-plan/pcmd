from fastp import device
from subprocess import PIPE, TimeoutExpired
import subprocess
import platform
import os
import signal
import sys

is_macos = "Darwin" in platform.system()


def popen(cmd_list):
    if is_macos:
        return subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE, shell=True,
                                preexec_fn=os.setsid, encoding='utf-8')
    else:
        return subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')


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


def adb_shell_input(serial_no, subcmd='', *args, source=''):
    """
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


def input_roll(serial_no, *args):
    """ roll <dx> <dy> (Default: trackball)"""
    adb_shell_input(serial_no, 'roll', *args, source='trackball')


def input_press(serial_no, *args):
    """ press(Default: trackball)"""
    adb_shell_input(serial_no, 'press', *args, source='trackball')


def input_tap(serial_no, *args):
    """tap <x> <y> (Default: touchscreen)"""
    adb_shell_input(serial_no, 'tap', *args, source='touchscreen')


def input_keyevent(serial_no, *args):
    """ keyevent [--longpress] <key code number or name> ... (Default: keyboard)
    keyevent map list: https://developer.android.com/reference/android/view/KeyEvent.html
    """
    adb_shell_input(serial_no, 'keyevent', *args, source='keyboard')


def input_text(serial_no, *args):
    """adb shell input text hello"""
    adb_shell_input(serial_no, 'text', *args, source='touchscreen')


def input_swipe(serial_no, *args):
    """swipe <x1> <y1> <x2> <y2> [duration(ms)] (Default: touchscreen)"""
    adb_shell_input(serial_no, 'swipe', *args)


def _capture_event(pipe, screen_width, screen_height, xmin, xmax, ymin, ymax):
    try:
        # i = 0
        line_y = ''
        line_x = ''
        for line in iter(lambda: pipe.stdout.readline(), ''):
            if 'ABS_MT_POSITION_X' in line:
                ABS_MT_POSITION_X = line.split(
                    "ABS_MT_POSITION_X")[-1].strip()
                raw_x = (int(ABS_MT_POSITION_X, 16) - xmin) * \
                        screen_width / (xmax - xmin)
                # print(ABS_MT_POSITION_X,int(ABS_MT_POSITION_X,16),raw_x)
                line_x = line.replace(ABS_MT_POSITION_X, str(raw_x))
                line = line.replace(ABS_MT_POSITION_X, str(raw_x))
            elif 'ABS_MT_POSITION_Y' in line:
                ABS_MT_POSITION_Y = line.split(
                    "ABS_MT_POSITION_Y")[-1].strip()
                raw_y = (int(ABS_MT_POSITION_Y, 16) - ymin) * \
                        screen_height / (ymax - ymin)
                line_y = line.replace(ABS_MT_POSITION_Y, str(raw_y))
                line = line.replace(ABS_MT_POSITION_Y, str(raw_y))
            elif 'BTN_TOUCH' in line and 'DOWN' in line:
                print('=' * 100)
                sys.stdout.write(line_x)
                sys.stdout.write(line_y)
                sys.stdout.write(line)
            elif 'BTN_TOUCH' in line and 'UP' in line:
                sys.stdout.write(line_x)
                sys.stdout.write(line_y)
                sys.stdout.write(line)
                pass
            # sys.stdout.write('[{}] {}'.format(i, line))
            # i += 1
    except KeyboardInterrupt as e:
        os.killpg(pipe.pid, signal.SIGINT)
    except TimeoutExpired as e:
        os.killpg(pipe.pid, signal.SIGINT)
        # out_bytes = pipe.communicate()[0]


def capture_event(serial_no):
    cmd = 'adb -s {}  shell getevent -lp'.format(serial_no)
    ret = os.popen(cmd).readlines()
    xmin = 0.0
    xmax = 0.0
    ymin = 0.0
    ymax = 0.0
    screen_width = 0.0
    screen_height = 0.0

    def get_value(the_line):
        elems = the_line.split(',')
        min_str = max_str = 0
        for e in elems:
            if 'min' in e:
                min_str = e.strip().split(" ")[1]
            elif 'max' in e:
                max_str = e.strip().split(" ")[1]
        return float(min_str), float(max_str)

    for line in ret[1:]:
        if 'ABS_MT_POSITION_X' in line:
            (xmin, xmax) = get_value(line)
        elif 'ABS_MT_POSITION_Y' in line:
            (ymin, ymax) = get_value(line)
    cmd = 'adb -s {}  shell wm size'.format(serial_no)
    ret = os.popen(cmd).readlines()[0].split(':')[1].strip().split('x')
    screen_width = float(ret[0].strip())
    screen_height = float(ret[1].strip())
    # print(xmin, xmax, ymin, ymax, screen_width, screen_height)
    # 360.3336422613531,1997.8537836682342
    cmd = 'adb -s {}  shell getevent -tl'.format(serial_no)
    with popen(cmd) as pipe:
        _capture_event(pipe, screen_width, screen_height,
                       xmin, xmax, ymin, ymax)


def main():
    d = device.get_devices()[0]
    # capture_event(device.get_devices()[0])
    # input_cmd(d, 'text', 'afdsf', 'adfafs')
    input_keyevent(d, '223')
    input_keyevent(d, '224')


if __name__ == '__main__':
    main()
