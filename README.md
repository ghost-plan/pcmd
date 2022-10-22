[![Python package](https://github.com/electrolyteJ/padb/actions/workflows/python-package.yml/badge.svg)](https://github.com/electrolyteJ/padb/actions/workflows/python-package.yml)

hi , padb

[pip install padb](https://pypi.org/project/padb/#description)

[pip install cmd-fwk](https://pypi.org/project/cmd-fwk/#description)


## Get Started
- pip install padb

- padb --help
```bash
usage: command line

positional arguments:
  {device-info,log-info}

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -s SERIAL_NO, --serial SERIAL_NO
                        use device with given serial

```

- padb device-info
```bash
usage: command line device-info [-h] [-b] [--top_activity] [-i]

optional arguments:
  -h, --help      show this help message and exit
  -b, --basic     device basic info
  --top_activity  top activity
  -i, --imei      get imei
```
padb device-info -b
```bash
[device-info:b/HONOR s/CUYDU19701014125 cid/A00000AD7B3287] >> parse_args Namespace(basic=True, func=<bound method BaseCommand.__execute of <pyadb.cmd.device_info.DeviceInfo object at 0x102d06f28>>, imei=False, serial_no='', top_activity=False)
[device-info:b/HONOR s/CUYDU19701014125 cid/A00000AD7B3287] >> execute
 [=     ] model:YAL-AL00
 [ =    ] brand:HONOR
 [  =   ] name:YAL-AL00
 [   =  ] wm size:(1080, 2340)
 [    = ] wm density:480
 [     =] android version:10
 [    = ] imei:A00000AD7B3287
 [   =  ] ip/mac:('192.168.1.102/24', '0x00001043')
 [  =   ] board:YAL
 [ =    ] abilist:['arm64-v8a', 'armeabi-v7a', 'armeabi']
 [=     ] cpu core size:8
 [ =    ] heap size/m:512

```
- padb log-info
```bash
usage: command line log-info [-h] [--tags TAGS]
                             [--format {none,brief,process,tag,raw,time,threadtime,long}]
                             [-e]

optional arguments:
  -h, --help            show this help message and exit
  --tags TAGS           tag
  --format {none,brief,process,tag,raw,time,threadtime,long}
                        format
  -e, --event           event
```

![log-info](/art/log-info.png)

## Framework

轻量级终端指令框架，`pip install cmd-fwk`即可在自己的项目接入。只要创建一个存放命令的文件夹cmds即可。

初始化框架
```python
import fwk,os
def entry():
    fwk.load_cmds(os.path.dirname(__file__), 'cmds')
```

在cmds目录下面编写自己的指令
```python
from fwk import BaseCommand
from fwk.device import (
    get_model, get_brand, get_name,
    get_wm_size, get_wm_density, get_android_version,
    get_imeis, get_ip_and_mac, get_board,
    get_abilist, get_cpu_core_size, get_heap_size,
)
from fwk.log import print_with_bar

class DeviceInfo(BaseCommand):
    #声明指令的功能
    def _create_parser(self, p):
        pyadb_parser = p.add_parser('device-info')
        pyadb_parser.add_argument('-b', '--basic', action='store_true',
                                  help='device basic info')
        pyadb_parser.add_argument('--top_activity', action='store_true',
                                  help='top activity')
        pyadb_parser.add_argument(
            '-i', '--imei', action='store_true', help='get imei')
        return pyadb_parser
    #获取指令中的数据
    def _parse_args(self, args: "ArgumentParser"):
        self.__basic = args.basic
    #执行指令的逻辑
    def _execute(self):
        if self.__basic:
            print_with_bar(0, 'model:', get_model(self._serial_no))
            print_with_bar(1, 'brand:', get_brand(self._serial_no))
            print_with_bar(2, 'name:', get_name(self._serial_no))
            print_with_bar(3, 'wm size:', get_wm_size(self._serial_no))
            print_with_bar(4, 'wm density:', get_wm_density(self._serial_no))
            print_with_bar(5, 'android version:',
                           get_android_version(self._serial_no))
            print_with_bar(6, 'imei:', get_imeis(self._serial_no))
            print_with_bar(7, 'ip/mac:', get_ip_and_mac(self._serial_no))
            print_with_bar(8, 'board:', get_board(self._serial_no))
            print_with_bar(9, 'abilist:', get_abilist(self._serial_no))
            print_with_bar(10, 'cpu core size:',
                           get_cpu_core_size(self._serial_no))
            print_with_bar(11, 'heap size/m:', get_heap_size(self._serial_no))

```

## Package Source Code

- pip3 install setuptools  ; pip3 install wheel
- python3 setup.py sdist bdist_wheel

## Upload Package

- pip3 install twine
- twine upload dist/*

## Reference:

[awesome adb](http://adbcommand.com/awesome-adb/cn)

[Android】ADB工具原理探究](https://itimetraveler.github.io/2019/06/07/Android%20ADB%E5%8E%9F%E7%90%86%E6%8E%A2%E7%A9%B6/#ADB%E7%AE%80%E4%BB%8B)

[python代码规范](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/)

小手动一动，支持一下独立开发者小电

技术公众号：吃地瓜的电解质

![qrcode_for_gh_7ee5cf10b1bf_258](https://user-images.githubusercontent.com/13391139/196029435-7b9f1bbe-3569-46e4-abe3-1625d51b9091.jpeg)

技术交流群：bundles assembler

![image](https://user-images.githubusercontent.com/13391139/196029947-a4d26595-7ff7-42f8-85c4-b46957309222.png)
