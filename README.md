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

- padb device-info -b
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
Usage: crawler command line

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SERIALNO, --serial=SERIALNO
                        use device with given serial
  --tags=TAGS           tag
  --format=FORMAT       format
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
