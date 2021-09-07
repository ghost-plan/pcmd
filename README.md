hi , pyadb

## get start
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
## package source code
- pip3 install setuptools  ; pip3 install wheel
- python3 setup.py sdist bdist_wheel
## upload package
- pip3 install twine
- twine upload dist/*
## reference:

[awesome adb](http://adbcommand.com/awesome-adb/cn)

[Android】ADB工具原理探究](https://itimetraveler.github.io/2019/06/07/Android%20ADB%E5%8E%9F%E7%90%86%E6%8E%A2%E7%A9%B6/#ADB%E7%AE%80%E4%BB%8B)

[python代码规范](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/)
