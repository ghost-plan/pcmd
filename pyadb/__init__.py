import sys
from pyadb.cmd import all_commands


def create_pyadb():
    arguments = sys.argv[1:]
    if arguments is None or len(arguments) == 0:
        sys.stdout.write('error: arguments is empty\n')
        return
    cmds = all_commands()

    for (subcmd_name, subcmd) in cmds.items():
        p, sp = subcmd.create_parser()
        subcmd.parse_args(p, sp, subcmd_name, arguments)
