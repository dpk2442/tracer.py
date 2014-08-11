# tracer.py

Parses stdin for Java exceptions and saves them to a database.

When run with stdin attached to a tty, it will display the errors in a curses interface.

## Examples

Parse stdin and save to a database:

    $ java ExceptionThrowingProgram 2>&1 | tracer.py tracer.db

Read the database file and display the errors in a curses interface:

    $ tracer.py tracer.db