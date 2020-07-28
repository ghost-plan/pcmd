ANSI_RED = "\u001B[31m"
ANSI_YELLOW = "\u001B[33m"
ANSI_GREEN = "\u001B[32m"
ANSI_BLUE = "\u001B[34m"
ANSI_RED_BACKGROUND = "\u001B[41m"
ANSI_GREEN_BACKGROUND = "\u001B[42m"
ANSI_YELLOW_BACKGROUND = "\u001B[43m"
ANSI_BLUE_BACKGROUND = "\u001B[44m"
ANSI_RESET = "\u001B[0m"
def error(*message):
    s = ''
    for i in message:
        s = s+str(i)
    print(ANSI_RED+s+ANSI_RESET)

def warn(*message):
    s = ''
    for i in message:
        s = s+str(i)
    print(ANSI_YELLOW+s+ANSI_RESET)

def info(*message):
    s = ''
    for i in message:
        s = s+str(i)
    print(ANSI_GREEN+s+ANSI_RESET)

def debug(*message):
    s = ''
    for i in message:
        s = s+str(i)
    print(ANSI_BLUE+s+ANSI_RESET)

def verbose(*message):
    s = ''
    for i in message:
        s = s+str(i)
    print(message)
