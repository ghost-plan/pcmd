from fastp import DeviceCommand
from fastp import event, log
from argparse import ArgumentParser


class LogInfo(DeviceCommand):
    def _create_parser(self, p):
        pyadb_parser = p.add_parser('log-info')
        pyadb_parser.add_argument(
            '--tags',
            dest="tags",
            action='append',
            default=[],
            help="tag"
        )
        pyadb_parser.add_argument(
            '--format',
            dest="format",
            choices=[
                log.Format.NONE.name.lower(),
                log.Format.BRIEF.name.lower(),
                log.Format.PROCESS.name.lower(),
                log.Format.TAG.name.lower(),
                log.Format.RAW.name.lower(),
                log.Format.TIME.name.lower(),
                log.Format.THREADTIME.name.lower(),
                log.Format.LONG.name.lower(),
            ],
            default=log.Format.NONE.name.lower(),
            help="format"
        )
        pyadb_parser.add_argument(
            '-e',
            '--event',
            action='store_true',
            default=False,
            help="event"
        )
        return pyadb_parser

    def _parse_args(self, args: ArgumentParser):
        self.__tags = args.tags
        f = args.format
        for e in log.Format:
            if f == e.name.lower():
                self.__format = e
                break
        self.__event = args.event

    def _execute(self):
        if self.__tags and self.__format:
            log.capture_log(self._serial_no, self.__tags, self.__format)
        elif self.__event:
            event.capture_event(self._serial_no)
