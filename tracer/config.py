import os
from configparser import ConfigParser

###################
## CONFIGURATION ##
###################

_defaultConfig = """\
# This serves as both a sample and a default confiuration for tracer.
# For tracer to read this file, save it to $HOME/.tracer.ini

# Main tracer configuration
# Supported colors: black, blue, cyan, green, magenta, red, white, yellow
[tracer]
    
    # command line error color highlighting
    highlightErrors = true
    errorColor = \033[0;31m
    
    # main screen colors
    backgroundColor = black
    foregroundColor = white
    backgroundInvertedColor = white
    foregroundInvertedColor = black
    
    # error highlighting
    backgroundErrorHighlightColor = black
    foregroundErrorHighlightColor = cyan

# Regular expression patterns to exclude errors from being saved.
# These patterns must match against the first line of the error message.
[excludePatterns]
    # example = ^[abc]+

# Regular expression patterns to highlight lines when viewing errors.
# These will be run against every line of the error.
[highlightPatterns]
    # example = java\.util
    pgbu = com\.oracle\.pgbu
"""

CONFIG_PATH = '.tracer.ini'
if 'HOME' in os.environ:
    CONFIG_PATH = os.environ['HOME'] + os.sep + CONFIG_PATH

def configToDict(config):
    d = {}
    for section in config.sections():
        d[section] = {}
        for item in config.items(section):
            d[section][item[0]] = item[1]
    return d


_defaults = ConfigParser()
_defaults.read_string(_defaultConfig)
config = ConfigParser()
config.read_dict(configToDict(_defaults))
if (os.path.exists(CONFIG_PATH)):
    config.read_file(open(CONFIG_PATH))

if __name__ == "__main__":
    print(_defaultConfig)