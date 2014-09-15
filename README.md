# tracer.py

Parses stdin for Java exceptions and saves them to a database.

When run with stdin attached to a tty, it will display the errors in a curses interface.

## Dependencies

### Required

- Python 3
- SQLite 3

### Optional

- Pyperclip (For copy functionality. Available through pip.)
  - If on Linux, `xclip` is recommended for pyperclip

## Configuration

Tracer uses an ini file for configuration. There are default values, but they can
be overriden by having a .tracer.ini in your $HOME folder.

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

## Examples

Parse stdin and save to a database:

    $ java ExceptionThrowingProgram 2>&1 | tracer.py tracer.db

Read the database file and display the errors in a curses interface:

    $ tracer.py tracer.db