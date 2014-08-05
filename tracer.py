#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses

class MainWin(object):

    def __init__(self, stdscr):
        self.window = stdscr
        self.isDetailPaneOpen = False
        self.detailPane = None
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.curs_set(0) # Hide cursor
        self.setupDataList(stdscr)
        self.redraw()
        self.listenForKeys()

    def setupDataList(self, stdscr):
        self.dataList = DataList(stdscr)
        for i in range(0, 100):
            detailPad = DetailPane(stdscr, "Data #{}\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\nhi\nreally really really really really really really really really long line wow i am way to good and typing the word really ok this still needs to be longer".format(i+1))
            self.dataList.addItem("Line {} of text.".format(i+1), detailPad)
        self.dataList.scrollBottom()

    def refresh(self):
        self.window.refresh()
        self.dataList.redraw()

    def redraw(self):
        screenLines, screenCols = self.window.getmaxyx()
        borderHorizontal = "─" * screenCols
        self.window.clear()
        self.window.addstr(0, 0, "Title Text".center(screenCols), curses.color_pair(1));
        if self.isDetailPaneOpen:
            self.window.addstr(5, 0, borderHorizontal, curses.color_pair(0))
        self.window.addstr(1, 0, borderHorizontal, curses.color_pair(0))
        self.window.addstr(screenLines - 2, 0, borderHorizontal, curses.color_pair(0))
        try:
            self.window.addstr(screenLines - 1, 0, " Footer Text".ljust(screenCols), curses.color_pair(1))
        except: pass
        self.refresh()
        if self.isDetailPaneOpen:
            self.detailPane.refresh()

    def listenForKeys(self):
        key = ''
        while (key != ord('q')):
            key = self.window.getch()
            # k or up arrow
            if key == ord('k') or key == curses.KEY_UP:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollUp()
                else:
                    self.detailPane.scrollUp()
            # j or down arrow
            elif key == ord('j') or key == curses.KEY_DOWN:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollDown()
                else:
                    self.detailPane.scrollDown()
            # h or left arrow
            elif key == ord('h') or key == curses.KEY_LEFT:
                if self.isDetailPaneOpen:
                    self.detailPane.scrollLeft()
            # l or right arrow
            elif key == ord('l') or key == curses.KEY_RIGHT:
                if self.isDetailPaneOpen:
                    self.detailPane.scrollRight()
            # n
            elif key == ord('n'):
                self.dataList.scrollDown()
                self.openDetailPane()
            # p
            elif key == ord('p'):
                self.dataList.scrollUp()
                self.openDetailPane()
            # g or home key
            elif key == ord('g') or key == curses.KEY_HOME:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollTop()
            # G or end key
            elif key == ord('G') or key == curses.KEY_END:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollBottom()
            # page up
            elif key == curses.KEY_NPAGE:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollPageUp()
            # page down
            elif key == curses.KEY_PPAGE:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollPageDown()
            # enter
            elif key == ord('\n'):
                if not self.isDetailPaneOpen:
                    self.openDetailPane()
                else:
                    self.closeDetailPane()

    def openDetailPane(self):
        self.isDetailPaneOpen = True
        self.detailPane = self.dataList.getSelection()[1]
        self.dataList.shrink()
        self.redraw()

    def closeDetailPane(self):
        self.isDetailPaneOpen = False
        self.detailPane = None
        self.dataList.grow()
        self.redraw()


class DataList(object):

    def __init__(self, parentWin):
        screensize       = parentWin.getmaxyx()
        self.screenLines = screensize[0] - 4
        self.MAX_LINES   = self.screenLines
        self.screenCols  = screensize[1]
        self.window      = parentWin.subwin(self.screenLines, self.screenCols, 2, 0)
        self.index       = 0
        self.screenPos   = 0
        self.items       = []
        self.itemData    = []
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

    def addItem(self, itemText, itemData):
        self.items.append(itemText)
        self.itemData.append(itemData)
        self.numItems += 1

    def getSelection(self):
        return (self.items[self.index], self.itemData[self.index])

    def _fixScroll(self):
        ''' Change the screePos without changing index so there is no whitespace after the last line. '''
        if self.index + (self.screenLines - self.screenPos) >= self.numItems:
            self.screenPos = self.screenLines - (self.numItems - self.index)
            self.redraw()

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
        self._fixScroll()

class DetailPane(object):

    def __init__(self, stdscr, data):
        screenSize = stdscr.getmaxyx()
        self.screenLines = screenSize[0] - 8
        self.screenCols = screenSize[1]
        self.linePos = 0
        self.colPos = 0
        self.numCols = 0
        data = data.split("\n")
        if isinstance(data, str):
            data = [data]
        self.numLines = len(data)
        for line in data:
            if len(line) > self.numCols:
                self.numCols = len(line)
        self.pad = curses.newpad(self.numLines, self.numCols)
        for i in range(self.numLines):
            try:
                self.pad.addstr(i, 0, data[i])
            except: pass

    def scrollDown(self):
        self.linePos += 1
        if self.linePos + self.screenLines >= self.numLines:
            self.linePos = self.numLines - self.screenLines
        self.refresh()

    def scrollUp(self):
        self.linePos -= 1
        if self.linePos < 0:
            self.linePos = 0
        self.refresh()

    def scrollRight(self):
        self.colPos += 1
        if self.colPos + self.screenCols >= self.numCols:
            self.colPos = self.numCols - self.screenCols
        self.refresh()

    def scrollLeft(self):
        self.colPos -= 1
        if self.colPos < 0:
            self.colPos = 0
        self.refresh()

    def refresh(self):
        self.pad.refresh(self.linePos,self.colPos, 6,0, self.screenLines+5,self.screenCols-1)

if __name__ == "__main__":
	curses.wrapper(MainWin)
