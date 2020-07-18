from executors import shell


def top_activity(devices):
    for device in devices:
        cmd = 'adb -s %s shell dumpsys activity activities | grep mResumedActivity' % device
        shell(cmd)


def open_app(serial_no, act):
    shell("adb -s "+serial_no + " shell am start -n {}".format(act))
