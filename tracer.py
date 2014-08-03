#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses

class Scroller(object):

    def __init__(self, parentWin):
        screensize       = parentWin.getmaxyx()
        self.screenLines = screensize[0] - 4
        self.MAX_LINES   = self.screenLines
        self.screenCols  = screensize[1]
        self.window      = parentWin.subwin(self.screenLines, self.screenCols, 2, 0)
        self.index       = 0
        self.screenPos   = 0
        self.items       = []
        self.numItems    = 0

        self.window.keypad(1)
    
    def redraw(self):
        self.window.clear()
        startIndex = self.index - self.screenPos
        if startIndex < 0: startIndex = 0
        endIndex = self.index + (self.screenLines - self.screenPos)
        if endIndex > self.numItems: endIndex = self.numItems
        lineCount = 0
        for i in range(startIndex, endIndex):
            if i == self.index:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            try:
                self.window.addstr(lineCount, 0, " " + self.items[i].ljust(self.screenCols - 1), mode)
            except: pass
            lineCount += 1
        self.window.refresh()

    def writeLine(self, line):
        self.items.append(line)
        self.numItems += 1

    def scrollUp(self):
        self.index -= 1
        self.screenPos -= 1
        if self.index < 0: self.index = 0
        if self.screenPos < 0: self.screenPos = 0
        self.redraw()
    
    def scrollDown(self):
        self.index += 1
        self.screenPos += 1
        if self.index >= self.numItems: self.index = self.numItems - 1
        if self.screenPos >= self.screenLines: self.screenPos = self.screenLines - 1
        self.redraw()

    def scrollTop(self):
        self.index = 0
        self.screenPos = 0
        self.redraw()

    def scrollBottom(self):
        self.index = self.numItems - 1
        self.screenPos = self.screenLines - 1
        self.redraw()

    def scrollPageUp(self):
        if self.index == 0: return
        self.index -= self.screenLines
        linesBeforeCurPos = self.screenPos - 1
        if self.index < 0:
            self.index = 0
            self.screenPos = 0
        elif self.index - linesBeforeCurPos < 0:
            self.index = linesBeforeCurPos + 1
        self.redraw()

    def scrollPageDown(self):
        if self.index == self.numItems - 1: return
        self.index += self.screenLines
        linesAfterCurPos = self.screenLines - self.screenPos - 1
        if self.index >= self.numItems:
            self.index = self.numItems - 1
            self.screenPos = self.screenLines - 1
        elif self.index + linesAfterCurPos >= self.numItems:
            self.index = self.numItems - linesAfterCurPos - 1
        self.redraw()

    def _resize(self, lines):
        # blank out window
        self.window.clear()
        self.window.refresh()
        # resize to smaller space and redraw
        self.window.resize(lines, self.screenCols)
        self.screenLines = lines
        # if screen pos off screen, move back
        if self.screenPos >= lines: self.screenPos = lines - 1
        self.redraw()

    def shrink(self):
        self._resize(3)

    def grow(self):
        self._resize(self.MAX_LINES)

def main(stdscr):
    # Hide cursor
    curses.curs_set(0)

    # Set up outer window
    screenLines, screenCols = stdscr.getmaxyx()
    borderHorizontal = "─" * screenCols
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    stdscr.addstr(0, 0, "Title Text".center(screenCols), curses.color_pair(1));
    stdscr.addstr(1, 0, borderHorizontal, curses.color_pair(0))
    stdscr.addstr(screenLines - 2, 0, borderHorizontal, curses.color_pair(0))
    try:
        stdscr.addstr(screenLines - 1, 0, " Footer Text".ljust(screenCols), curses.color_pair(1))
    except: pass

    scroller = Scroller(stdscr)

    for i in range(0, 100):
        scroller.writeLine("Line {} of text.".format(i+1))
    scroller.scrollBottom()

    stdscr.refresh()
    scroller.redraw()

    key = ''
    while (key != ord('q')):
        key = stdscr.getch()
        if key == ord('k') or key == curses.KEY_UP:
            scroller.scrollUp()
        elif key == ord('j') or key == curses.KEY_DOWN:
            scroller.scrollDown()
        elif key == ord('g') or key == curses.KEY_HOME:
            scroller.scrollTop()
        elif key == ord('G') or key == curses.KEY_END:
            scroller.scrollBottom()
        elif key == curses.KEY_NPAGE: # page up
            scroller.scrollPageUp()
        elif key == curses.KEY_PPAGE: # page down
            scroller.scrollPageDown()
        elif key == ord('s'):
            scroller.shrink()

if __name__ == "__main__":
	curses.wrapper(main)
