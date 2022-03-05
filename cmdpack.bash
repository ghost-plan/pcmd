
echo y|pip3 uninstall padb
python3 cmdsetup.py sdist bdist_wheel
pip3 install dist/padb-1.2.0-py3-none-any.whl
padb device-info --help