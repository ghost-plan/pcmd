import time
import re
import sys
import os
import functools
from subprocess import TimeoutExpired, PIPE, DEVNULL, STDOUT, PIPE
import subprocess
import platform
import socket

is_macos = "Darwin" in platform.system()
ENCODING = 'utf-8'
DEFAULT_ENCODING = ENCODING
HOST = '127.0.0.1'
PORT = 5037


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


def popen(cmd_list):
    if is_macos:
        return subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE, shell=True,
                                preexec_fn=os.setsid, encoding='utf-8')
    else:
        return subprocess.Popen(cmd_list, stdout=PIPE, stderr=PIPE, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')


def adb_shell(serial_no, cmd):
    return run('adb -s %s shell %s' % (serial_no, cmd))


def adb_shell_input(serial_no, subcmd, *args, source=''):
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


def adb_shell_am(serial_no):
    pass


def adb_shell_pm(serial_no):
    ''' adb shell pm list packages [-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]'''
    pass


def adb_shell_getprop(serial_no):
    pass


def adb_shell_dumpsys(serial_no):
    pass


def adb_push(serial_no, src, dest):
    return run('adb -s %s push %s %s' % (serial_no, src, dest))


def adb_pull(serial_no, src, dest):
    return run('adb -s %s pull %s %s' % (serial_no, src, dest))


# ============================================ adb  connect ========================================================

def encode_data(data):
    """ message we sent to server contains 2 parts
        1. length
        2. content
    """
    byte_data = data.encode(DEFAULT_ENCODING)
    byte_length = "{0:04X}".format(len(byte_data)).encode(DEFAULT_ENCODING)
    return byte_length + byte_data


def read_all_content(target_socket):
    """ and, message we got also contains 3 parts:
        1. status (4)
        2. length (4)
        3. content (unknown)
    """
    result = b''
    while True:
        buf = target_socket.recv(1024)
        if not len(buf):
            return result
        result += buf


def adb_client_start():
    """
    create socket and connect to adb server https://android.googlesource.com/platform/system/core/+/jb-dev/adb/SERVICES.TXT
    """
    with socket.socket() as skt:
        skt.connect((HOST, PORT))
        while True:
            try:
                ready_data = encode_data('host:devices')
                skt.send(ready_data)
                status = skt.recv(4)
                length = skt.recv(4)
                devices = read_all_content(skt)
                final_result = {
                    'status': status,
                    'length': length,
                    'devices': devices,
                }
                final_result = {_: v.decode(DEFAULT_ENCODING)
                                for _, v in final_result.items()}
                print(final_result)
                time.sleep(30)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt:', e)
                skt.close()
                break
            except ConnectionError as _:
                pass
            except BaseException as e:
                print('BaseException:', e)
                skt.close()
                break


'''
networking:
 connect HOST[:PORT]      connect to a device via TCP/IP [default port=5555]
 disconnect [HOST[:PORT]]
     disconnect from given TCP/IP device [default port=5555], or all
 pair HOST[:PORT] [PAIRING CODE]
     pair with a device for secure TCP/IP communication
 forward --list           list all forward socket connections
 forward [--no-rebind] LOCAL REMOTE
     forward socket connection using:
       tcp:<port> (<local> may be "tcp:0" to pick any open port)
       localabstract:<unix domain socket name>
       localreserved:<unix domain socket name>
       localfilesystem:<unix domain socket name>
       dev:<character device name>
       jdwp:<process pid> (remote only)
       acceptfd:<fd> (listen only)
 forward --remove LOCAL   remove specific forward socket connection
 forward --remove-all     remove all forward socket connections
 ppp TTY [PARAMETER...]   run PPP over USB
 reverse --list           list all reverse socket connections from device
 reverse [--no-rebind] REMOTE LOCAL
     reverse socket connection using:
       tcp:<port> (<remote> may be "tcp:0" to pick any open port)
       localabstract:<unix domain socket name>
       localreserved:<unix domain socket name>
       localfilesystem:<unix domain socket name>
 reverse --remove REMOTE  remove specific reverse socket connection
 reverse --remove-all     remove all reverse socket connections from device
 mdns check               check if mdns discovery is available
 mdns services            list all discovered services
'''


class AdbServer:
    """
    adb reverse  localabstract:river tcp:27184
    """

    def __init__(self) -> None:
        super().__init__()

def read_input(sock,len,rea):
    pass
class AdbClient:
    """
    adb forward localabstract
    connect --> select_service('host:transport:device’) -> select_service('localabstract:bbb’)
    """

    def __init__(self) -> None:
        super().__init__()

    def connect_to_device(self, device=None, port=5037):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', port))
        self.sock = sock

        try:
            if device is None:
                self.select_service('host:transport-any')
            else:
                self.select_service('host:transport:%s' % (device))

        except SelectServiceError as e:
            raise HumanReadableError(
                'Failure to target device %s: %s' % (device, e.reason))

    def select_service(self, service):
        message = '%04x%s' % (len(service), service)
        self.sock.send(message.encode('ascii'))
        status = read_input(self.sock, 4, "status")
        if status == b'OKAY':
            # All good...
            pass
        elif status == b'FAIL':
            reason_len = int(read_input(self.sock, 4, "fail reason"), 16)
            reason = read_input(self.sock, reason_len,
                                "fail reason lean").decode('ascii')
            raise SelectServiceError(reason)
        else:
            raise Exception('Unrecognized status=%s' % (status))


def get_adb_server_port_from_server_socket():
    socket_spec = os.environ.get('ADB_SERVER_SOCKET')
    if not socket_spec:
        return None
    if not socket_spec.startswith('tcp:'):
        raise HumanReadableError(
            'Invalid or unsupported socket spec \'%s\' specified in ADB_SERVER_SOCKET.' % (
                socket_spec))
    return socket_spec.split(':')[-1]


def get_adb_server_port():
    defaultPort = 5037
    portStr = get_adb_server_port_from_server_socket(
    ) or os.environ.get('ANDROID_ADB_SERVER_PORT')
    if portStr is None:
        return defaultPort
    elif portStr.isdigit():
        return int(portStr)
    else:
        raise HumanReadableError(
            'Invalid integer \'%s\' specified in ANDROID_ADB_SERVER_PORT or ADB_SERVER_SOCKET.' % (
                portStr))


class SelectServiceError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class HumanReadableError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


def main():
    pass


# adb_client_start()


if __name__ == '__main__':
    main()
