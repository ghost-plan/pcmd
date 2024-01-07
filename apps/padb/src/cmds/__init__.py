__version__ = '1.0.0'
import fastp,os
def entry():
    fastp.load_cmds(os.path.dirname(__file__), 'cmds')
