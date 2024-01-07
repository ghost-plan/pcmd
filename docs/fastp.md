[pip install cmd-fastp](https://pypi.org/project/cmd-fastp/#description)

## Framework

轻量级终端指令框架，`pip install cmd-fastp`即可在自己的项目接入。只要创建一个存放命令的文件夹cmds即可。

初始化框架
```python
import fastp,os
def entry():
    fastp.load_cmds(os.path.dirname(__file__), 'cmds')
```

在cmds目录下面编写自己的指令

```python
from fastp import BaseCommand
from fastp import (
    get_model, get_brand, get_name,
    get_wm_size, get_wm_density, get_android_version,
    get_imeis, get_ip_and_mac, get_board,
    get_abilist, get_cpu_core_size, get_heap_size,
)
from fastp import print_with_bar


class DeviceInfo(BaseCommand):
    # 声明指令的功能
    def _create_parser(self, p):
        pyadb_parser = p.add_parser('device-info')
        pyadb_parser.add_argument('-b', '--basic', action='store_true',
                                  help='device basic info')
        pyadb_parser.add_argument('--top_activity', action='store_true',
                                  help='top activity')
        pyadb_parser.add_argument(
            '-i', '--imei', action='store_true', help='get imei')
        return pyadb_parser

    # 获取指令中的数据
    def _parse_args(self, args: "ArgumentParser"):
        self.__basic = args.basic

    # 执行指令的逻辑
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