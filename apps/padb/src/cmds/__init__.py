__version__ = '1.0.0'
import fwk,os
def entry():
    fwk.load_cmds(os.path.dirname(__file__), 'cmds')
