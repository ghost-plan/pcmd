from cmd import BaseCommand
import sys
from pyadb import log
class LogInfo(BaseCommand):
    def _optionParser(self, parser):
        parser.add_option(
            '--tags',
            dest="tags",
            action='append',
            default=[], 
            help="tag"
        )
        parser.add_option(
            '--format',
            dest="format",
            type='choice',
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

    def _parse_args(self, parser_options, arguments):
        self.__tags = parser_options.tags
        f  = parser_options.format
        for e in log.Format:
            if f == e.name.lower():
                self.__format = e
                break

    def _execute(self):
        log.capture_log('a6426ab6',self.__tags,self.__format)
