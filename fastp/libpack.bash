
echo y|pip3 uninstall  cmd-fastp
python3 libsetup.py sdist bdist_wheel
pip3 install dist/cmd_fwk-1.2.2-py3-none-any.whl