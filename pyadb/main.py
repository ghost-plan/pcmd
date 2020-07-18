import sys
from cmd import all_commands


def main(arguments=None):
    if arguments[0] is None:
        sys.stdout.write('error: arguments is empty\n')
        return
    cmds = all_commands()
    for (subcmd_name, subcmd) in cmds.items():
        if subcmd_name in arguments:
            p, sp = subcmd.create_parser()
            subcmd.parse_args(p, sp, subcmd_name, arguments)
            break


if __name__ == '__main__':
    main(sys.argv[1:])
