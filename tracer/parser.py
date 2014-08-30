import re
import sys
from tracer.config import config

###########
## UTILS ##
###########

_excludePatterns = config["excludePatterns"]
EXCLUDE_PATTERNS = []
for key in _excludePatterns:
    pattern = _excludePatterns[key]
    try:
        EXCLUDE_PATTERNS.append(re.compile(pattern))
    except:
        raise Exception("Error compiling regex " + key)

def isExcludedError(s):
    for pattern in EXCLUDE_PATTERNS:
        if (pattern.search(s)): return True
    return False


#############################
## PARSES STDIN FOR ERRORS ##
#############################

ERROR_START = re.compile(r".*?ERROR")
ERROR_MORE = re.compile(r"^... [0-9]*? more$")
BLANK_LINE = re.compile(r"^\s*$")
class StdinParser(object):
    def __init__(self, db):
        self.db = db
        self.inError = False
        self.hasReadException = False
        self.errorBuffer = []
        for line in sys.stdin:
            self.parseError(line)
            if self.inError:
                self.printErrorLine(line)
            else:
                self.printLogLine(line)

    def parseError(self, line):
        if self.inError:
            if line.startswith("<") or (self.hasReadAt and not self.isContinuePattern(line)):
                self.flushError()
                self.inError = False
            self.hasReadAt = line.startswith("at ")
            #if line.startswith("at ") and not self.hasReadAt:
            #    self.hasReadAt = True
        if ERROR_START.search(line):
            if isExcludedError(line):
                self.inError = False
                return
            self.flushError()
            # print("\n>>>>> ERROR START\n")
            self.inError = True
            self.hasReadAt = False

    def isContinuePattern(self, line):
        return \
            line.startswith("at ") or \
            line.startswith("Caused by: ") or \
            ERROR_MORE.match(line) or \
            BLANK_LINE.match(line)

    def flushError(self):
        if self.errorBuffer:
            shortErrorText = self.errorBuffer[0]
            fullErrorText = ''.join(self.errorBuffer)
            self.db.addError(shortErrorText, fullErrorText)
            self.errorBuffer[:] = [] # python clear list magic
            # print("\n<<<<< ERROR END\n")

    def printLogLine(self, line):
        print(line, end="")

    def printErrorLine(self, line):
        self.errorBuffer.append(line)
        if (config.getboolean("tracer", "highlightErrors")):
            print(config["tracer"]["errorColor"], line, "\033[0;0m", sep="", end="")
        else:
            print(line, end="")