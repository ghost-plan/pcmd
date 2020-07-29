from pyadb.cmd import BaseCommand
import sys
from pyadb import log
class LogInfo(BaseCommand):
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
        return pyadb_parser

    def _parse_args(self, args):
        self.__tags = args.tags
        f  = args.format
        for e in log.Format:
            if f == e.name.lower():
                self.__format = e
                break

    def _execute(self):
        log.capture_log('a6426ab6',self.__tags,self.__format)
        pass
