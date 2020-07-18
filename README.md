hi , pyadb

## get start
- pip install padb

- padb --help
```bash
usage: command line

positional arguments:
  {device-info}

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -s SERIAL_NO, --serial SERIAL_NO
                        use device with given serial

```
## package source code
- pip3 install setuptools  ; pip3 install wheel
- python3 setup.py sdist bdist_wheel
## upload package
- pip3 install twine
- twine upload dist/*
## reference:
[awesome adb](http://adbcommand.com/awesome-adb/cn)