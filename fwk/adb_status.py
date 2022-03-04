from multiprocessing.connection import Client, Listener, wait, Pipe
from multiprocessing import Queue, Process, Pool, Process, Lock, Value, Array, Manager
import socket
import time
import os
#=====================================pip and queue===============================================================
switch_to_queue = False
parent_conn, child_conn = Pipe()
queue = Queue()
address = ('localhost', 6000)
family = 'AF_UNIX'

def server_start(child_conn=None, queue=None):
    def task(conn):
        print('server side start')
        # if switch_to_queue and queue:
        #     for i in range(0,10):
        #         queue.put('[queue] coming from server side')
        #         time.sleep(1)
        # elif conn:
        #     for i in range(0,10):
        #         conn.send('[pip] coming from server side...{}'.format(i))
        #         time.sleep(0.3)
        #     conn.send('exit')

        with Client(address) as client:
            for i in range(0, 10):
                client.send('push {} msg to client '.format(i))

    p = Process(target=task, args=(child_conn,))
    p.start()
    # p.join()
    # with ProcessPoolExecutor() as proc_exe:
    #     proc_exe.submit(task)


def client_start(conn=None, queue=None):
    print('client side start')
    result = None
    # while True:
    #     if switch_to_queue and queue:
    #         result = queue.get()
    #     elif conn:
    #         result = conn.recv()
    #         print('result:',result)
    #         if 'exit' in result:
    #             break

    with Listener(address) as listener:
        with listener.accept() as conn:
            while True:
                try:
                    ret = conn.recv()
                except EOFError as e:
                    print('error:', e.__cause__)
                    break
                else:
                    print('result:', ret)
    print('client side end')
#============================================ socket ========================================================

HOST = '127.0.0.1'
PORT = 5037
ENCODING = 'utf-8'
DEFAULT_ENCODING = ENCODING

def socket_client_start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
    print('Received', repr(data))


def socket_server_start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
#============================================ adb  ========================================================
def encode_data(data):
    ''' message we sent to server contains 2 parts
        1. length
        2. content
    '''
    byte_data = data.encode(DEFAULT_ENCODING)
    byte_length = "{0:04X}".format(len(byte_data)).encode(DEFAULT_ENCODING)
    return byte_length + byte_data


def read_all_content(target_socket):
    ''' and, message we got also contains 3 parts:
        1. status (4)
        2. length (4)
        3. content (unknown)
    '''
    result = b''
    while True:
        buf = target_socket.recv(1024)
        if not len(buf):
            return result
        result += buf
def adb_client_start():
    """ create socket and connect to adb server https://android.googlesource.com/platform/system/core/+/jb-dev/adb/SERVICES.TXT"""
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
                final_result = {_: v.decode(DEFAULT_ENCODING) for _, v in final_result.items()}
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
class AdbServer():
    '''
    adb reverse  localabstract:river tcp:27184
    '''
    def __init__(self) -> None:
        super().__init__()

class AdbClient():
    '''
    adb forward localabstract
    connect --> select_service('host:transport:device’) -> select_service('localabstract:bbb’)
    '''
    def __init__(self) -> None:
        super().__init__()

    def connect_to_device(self,device=None, port=5037):
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
            reason = read_input(self.sock, reason_len, "fail reason lean").decode('ascii')
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
  portStr = get_adb_server_port_from_server_socket() or os.environ.get('ANDROID_ADB_SERVER_PORT')
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
    # server_start(child_conn, queue)
    # client_start(parent_conn, queue)
    # socket_client_start()
    # socket_server_start()
    # adb_client_start()




if __name__ == '__main__':
    main()
