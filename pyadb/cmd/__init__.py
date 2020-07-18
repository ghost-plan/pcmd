__version__ = "1.0.0"
__release_date__ = "15-Jun-2020"
import re
import argparse
import os
import subprocess
from importlib import import_module
import sys
from argparse import ArgumentParser


class BaseCommand(object):
    # _arg_parser = None
    # _subparsers = None
    _serial_no = ''
    _app_client_code = ''
    _brand = ''
    _subcmd_name = None

    def create_parser(self):
        parser = argparse.ArgumentParser(
            usage="command line",
            description=__doc__,
        )
        parser.add_argument('--version', action='version', version='1.0.0')
        parser.add_argument('-s', '--serial', dest='serial_no', default='',
                            help='use device with given serial')
        subparsers = parser.add_subparsers()
        sp = self._create_parser(subparsers)
        return parser, sp

    def _create_parser(self, p) -> ArgumentParser:
        pass

    def print_with_cmd(self, content):
        s = 'b/{} s/{} cid/{}'.format(self._brand, self._serial_no,
                                      self._app_client_code)
        print('[{}:{}] >> {}'.format(self._subcmd_name, s, content))

    def parse_args(self, parser, subparser, subcmd_name, arguments):
        subparser.set_defaults(func=self.__execute)
        self._subcmd_name = subcmd_name
        args = parser.parse_args()
    #    self.print_with_cmd(arguments)
        serial_no = args.serial_no.strip()
        if len(serial_no) == 0:
            devices = self.get_devices()
            device_size = len(devices)
            if device_size == 1:
                serial_no = devices[0]
            elif device_size >= 2:
                raise BaseException("有多台需要指定设备 {}".format(devices))
            else:
                raise BaseException("没有设备连接")

        self._serial_no = serial_no
        self._app_client_code = self.get_app_client_code(serial_no)
        if len((self._app_client_code)) == 0:
            sys.exit(0)
            pass
        self._brand = os.popen("adb -s " + self._serial_no +
                               "  shell getprop ro.product.brand").readlines()[0].strip()
        self.print_with_cmd('parse_args {}'.format(args))
        self._parse_args(args)
        # start execute
        args.func()

    def _parse_args(self, args):
        pass

    def get_app_client_code(self, serialNo):
        ret = os.popen(
            'adb -s {} shell service call iphonesubinfo 1'.format(serialNo)).readlines()
        client_code = ''
        for line in ret[1:]:
            client_code += line.split("'")[1].replace('.', "").strip()
        return client_code

    def __execute(self):
        self.print_with_cmd('execute')
        self._execute()

    def _execute(self):
        pass

    def check_device(self, device):
        if device in self.get_devices():
            return True
        else:
            return False

    def get_devices(self):
        devices = []
        ret = os.popen("adb devices").readlines()

        for line in ret[1:]:
            if (re.match(".*device$", line)):
                devices.append(line.split("\t")[0])
        return devices


my_dir = os.path.dirname(__file__)


def all_commands():
    all_commands = {}
    for file in os.listdir(my_dir):
        if file == '__init__.py' or not file.endswith('.py'):
            continue
        py_filename = file[:-3]

        clsn = py_filename.capitalize()
        while clsn.find('_') > 0:
            h = clsn.index('_')
            clsn = clsn[0:h] + clsn[h + 1:].capitalize()
        module = import_module('.{}'.format(py_filename), package='pyadb.cmd')
        try:
            cmd = getattr(module, clsn)()
        except AttributeError as identifier:
            pass
            # raise SyntaxError('%s/%s does not define class %s' % (
            #                  __name__, file, clsn))
        name = py_filename.replace('_', '-')
        cmd.NAME = name
        all_commands[name] = cmd
    return all_commands
