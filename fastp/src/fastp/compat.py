import os
import subprocess
from subprocess import Popen, PIPE
from fastp import is_macos


# os.system()
# os.popen()
def popen(cmd):
    if is_macos:
        return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                     preexec_fn=os.setsid, encoding='utf-8')
    else:
        return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')
