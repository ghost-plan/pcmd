__version__ = "1.0.0"
__release_date__ = "15-Jun-2020"

import argparse
import os
from importlib import import_module
import sys
from argparse import ArgumentParser
from fastp import device, log
from abc import abstractmethod, ABC


class BaseCommand(ABC):
    # _arg_parser = None
    # _subparsers = None

    @staticmethod
    def create():
        parser = argparse.ArgumentParser(
            usage="command line",
            description=__doc__,
        )
        parser.add_argument('--version', action='version', version='1.0.0')
        parser.add_argument('-s', '--serial', dest='serial_no', default='',
                            help='use device with given serial')
        sps = parser.add_subparsers()
        return parser, sps

    @staticmethod
    def start(p):
        args = p.parse_args()
        args.func(args)

    def create_parser(self, p, sps) -> ArgumentParser:
        return self._create_parser(sps)

    def parse_args(self, subparser, subcmd_name):
        subparser.set_defaults(func=self.parse_args_internal)
        self._subcmd_name = subcmd_name

    def parse_args_internal(self, args):
        self._parse_args(args)
        # self.print_with_cmd('parse_args {}'.format(args))
        self.execute_internal()

    def execute_internal(self):
        self._execute()

    @abstractmethod
    def _create_parser(self, p) -> ArgumentParser:
        pass

    @abstractmethod
    def _parse_args(self, args):
        pass

    @abstractmethod
    def _execute(self):
        pass


class Lazy:
    """懒加载，kotlin中的by lazy关键字"""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, clz):
        if not instance:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class DeviceCommand(BaseCommand):
    _serial_no = ''

    @Lazy
    def _brand(self):
        return device.get_brand(self._serial_no)

    @Lazy
    def _imeis(self):
        return device.get_imeis(self._serial_no)
        # print('imeis:'+str(self._imeis))
        # if len(self._imeis) == 0:
        # log.error('not found imeis')
        # sys.exit(1)

    def print_with_cmd(self, *content):
        s = ''
        for i in content:
            s = s + str(i)
        device_info = 's/{} imeis/{} b/{}'.format(
            self._serial_no, self._imeis, self._brand)
        log.info('[ {} ] {} >> {}'.format(self._subcmd_name, device_info, s))

    def parse_args_internal(self, args):
        serial_no = args.serial_no
        if len(serial_no) == 0:
            devices = device.get_devices()
            device_size = len(devices)
            if device_size == 1:
                serial_no = devices[0]
            elif device_size >= 2:
                #                 raise BaseException("有多台需要指定设备 {}".format(devices))
                log.error("有多台需要指定设备 {}".format(devices))
                sys.exit(1)
            else:
                #                 raise BaseException("没有设备连接")
                log.error("没有设备连接")
                sys.exit(1)
        self._serial_no = serial_no
        super().parse_args_internal(args)

    def execute_internal(self):
        self.print_with_cmd('execute doing ...')
        self._execute()


def all_commands(cmd_dir, pkg):
    all_commands = {}
    for file in os.listdir(cmd_dir):
        if file == '__init__.py' or file == 'main.py' or not file.endswith('.py'):
            continue
        py_filename = file[:-3]
        clsn = py_filename.capitalize()
        while clsn.find('_') > 0:
            h = clsn.index('_')
            clsn = clsn[0:h] + clsn[h + 1:].capitalize()
        # modulename = os.path.basename(cmd_dir) +'.'+py_filename
        try:
            module = import_module('.' + py_filename, pkg)
        except ModuleNotFoundError as e:
            print(pkg + "." + py_filename + " 导入失败")
            raise e
        try:
            cmd = getattr(module, clsn)()
        except AttributeError as identifier:
            pass
            raise SyntaxError('%s/%s does not define class %s' % (
                __name__, file, clsn))
        name = py_filename.replace('_', '-')
        cmd.NAME = name
        all_commands[name] = cmd
    return all_commands


def load_cmds(cmd_dir, pkg):
    arguments = sys.argv[1:]
    if arguments is None or len(arguments) == 0:
        sys.stdout.write('error: arguments is empty\n')
        return
    cmds = all_commands(cmd_dir, pkg)
    p, sps = BaseCommand.create()
    for (subcmd_name, subcmd) in cmds.items():
        sp = subcmd.create_parser(p, sps)
        subcmd.parse_args(sp, subcmd_name)
    BaseCommand.start(p)
