from enum import Enum, unique
import platform
import sys


@unique
class PyVersion(Enum):
    v2 = 0
    v3 = 1


@unique
class Os(Enum):
    MAC_OS = 0
    WINDOWS = 1
    LINUX = 2


is_python3 = (sys.version_info[0] == 3)

is_macos = "Darwin" in platform.system()
