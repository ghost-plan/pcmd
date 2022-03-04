
echo y|pip3 uninstall  cmd-fwk
python3 libsetup.py sdist bdist_wheel
pip3 install dist/cmd_fwk-1.1.0-py3-none-any.whl