#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import sys
from tracer.common import DBManager
from tracer.config import config


def closeDB(db):
    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " dbFile")
        exit()
    db = DBManager(sys.argv[1])
    atexit.register(closeDB, db)
    if sys.stdin.isatty():
        from curses import wrapper
        from tracer.view import MainWin
        wrapper(MainWin, db)
    else:
        from tracer.parser import StdinParser
        try:
            StdinParser(db)
        except KeyboardInterrupt: pass
