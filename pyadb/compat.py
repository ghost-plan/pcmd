import platform,os
import subprocess
from subprocess import Popen, PIPE
def __is_macos():
    return True if "Darwin" in platform.system() else False


def popen(cmd):
    if __is_macos():
        return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                   preexec_fn=os.setsid, encoding='utf-8')
    else:
        return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,
                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, encoding='utf-8')
