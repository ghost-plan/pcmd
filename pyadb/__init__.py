import sys
from pyadb.cmd import all_commands,BaseCommand


def create_pyadb():
    arguments = sys.argv[1:]
    if arguments is None or len(arguments) == 0:
        sys.stdout.write('error: arguments is empty\n')
        return
    cmds = all_commands()
    p,sps = BaseCommand.create()
    for (subcmd_name, subcmd) in cmds.items():
        sp = subcmd.create_parser(p,sps)
        subcmd.parse_args(sp, subcmd_name)
    BaseCommand.start(p)

