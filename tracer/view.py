import curses
import re
from tracer.config import config

##################
## CURSES UTILS ##
##################

REGULAR_COLORS = 1
INVERTED_COLORS = 2
ERROR_HIGHLIGHT_COLORS = 3

def getCursesColor(s):
    s = s.lower()
    if   s == "black":   return curses.COLOR_BLACK
    elif s == "blue":    return curses.COLOR_BLUE
    elif s == "cyan":    return curses.COLOR_CYAN
    elif s == "green":   return curses.COLOR_GREEN
    elif s == "magenta": return curses.COLOR_MAGENTA
    elif s == "red":     return curses.COLOR_RED
    elif s == "white":   return curses.COLOR_WHITE
    elif s == "yellow":  return curses.COLOR_YELLOW
    return curses.COLOR_BLACK

_highlightPatterns = config["highlightPatterns"]
ERROR_HIGHLIGHT_PATTERNS = []
for key in _highlightPatterns:
    pattern = _highlightPatterns[key]
    try:
        ERROR_HIGHLIGHT_PATTERNS.append(re.compile(pattern))
    except:
        raise Exception("Error compiling regex " + key)

def isHighlightedErrorLine(s):
    for pattern in ERROR_HIGHLIGHT_PATTERNS:
        if (pattern.search(s)): return True
    return False


########################
## MAIN WINDOW OBJECT ##
########################

class MainWin(object):

    def __init__(self, stdscr, db):
        self.window = stdscr
        self.db = db
        self.isDetailPaneOpen = False
        self.detailPane = DetailPane(stdscr)
        # colors
        foregroundColor = getCursesColor(config["tracer"]["foregroundColor"])
        backgroundColor = getCursesColor(config["tracer"]["backgroundColor"])
        curses.init_pair(REGULAR_COLORS, foregroundColor, backgroundColor)
        # inverted colors
        foregroundInvertedColor = getCursesColor(config["tracer"]["foregroundInvertedColor"])
        backgroundInvertedColor = getCursesColor(config["tracer"]["backgroundInvertedColor"])
        curses.init_pair(INVERTED_COLORS, foregroundInvertedColor, backgroundInvertedColor)
        # error highlight colors
        foregroundErrorHighlightColor = getCursesColor(config["tracer"]["foregroundErrorHighlightColor"])
        backgroundErrorHighlightColor = getCursesColor(config["tracer"]["backgroundErrorHighlightColor"])
        curses.init_pair(ERROR_HIGHLIGHT_COLORS, foregroundErrorHighlightColor, backgroundErrorHighlightColor)
        curses.curs_set(0) # Hide cursor
        self._setupDataList(stdscr)
        self._redraw()
        self._listenForKeys()

    def _setupDataList(self, stdscr):
        self.dataList = DataList(stdscr)
        for error in self.db.fetchErrors():
            self.dataList.addItem(error.getListText(), error.id)
        self.dataList.scrollBottom()

    def refresh(self):
        self.window.refresh()
        self.dataList.redraw()

    def _redraw(self):
        screenLines, screenCols = self.window.getmaxyx()
        borderHorizontal = "─" * screenCols
        self.window.clear()
        self.window.addstr(0, 0, "Tracer".center(screenCols), curses.color_pair(INVERTED_COLORS));
        if self.isDetailPaneOpen:
            self.window.addstr(5, 0, borderHorizontal, curses.color_pair(REGULAR_COLORS))
        self.window.addstr(1, 0, borderHorizontal, curses.color_pair(REGULAR_COLORS))
        self.window.addstr(screenLines - 2, 0, borderHorizontal, curses.color_pair(REGULAR_COLORS))
        if self.isDetailPaneOpen:
            footerText = "n - next error, p - previous error, enter - close error, up/down/left/right - scroll error, q - quit"
        else:
            footerText = "j/n/down arrow - next error, k/p/up arrow - previous error, enter - open error, r - reload, q - quit"
        try:
            self.window.addstr(screenLines - 1, 0, (" " + footerText).ljust(screenCols), curses.color_pair(INVERTED_COLORS))
        except: pass
        self.refresh()
        if self.isDetailPaneOpen:
            self.detailPane.refresh()

    def _listenForKeys(self):
        key = ""
        while (key != ord("q")):
            key = self.window.getch()
            # k or up arrow
            if key == ord("k") or key == curses.KEY_UP:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollUp()
                else:
                    self.detailPane.scrollUp()
            # j or down arrow
            elif key == ord("j") or key == curses.KEY_DOWN:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollDown()
                else:
                    self.detailPane.scrollDown()
            # h or left arrow
            elif key == ord("h") or key == curses.KEY_LEFT:
                if self.isDetailPaneOpen:
                    self.detailPane.scrollLeft()
            # l or right arrow
            elif key == ord("l") or key == curses.KEY_RIGHT:
                if self.isDetailPaneOpen:
                    self.detailPane.scrollRight()
            # n
            elif key == ord("n"):
                self.dataList.scrollDown()
                self.openDetailPane()
            # p
            elif key == ord("p"):
                self.dataList.scrollUp()
                self.openDetailPane()
            # g or home key
            elif key == ord("g") or key == curses.KEY_HOME:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollTop()
                else:
                    self.detailPane.scrollTop()
            # G or end key
            elif key == ord("G") or key == curses.KEY_END:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollBottom()
                else:
                    self.detailPane.scrollBottom()
            # page up
            elif key == curses.KEY_PPAGE:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollPageUp()
                else:
                    self.detailPane.scrollPageUp()
            # page down
            elif key == curses.KEY_NPAGE:
                if not self.isDetailPaneOpen:
                    self.dataList.scrollPageDown()
                else:
                    self.detailPane.scrollPageDown()
            # enter
            elif key == ord("\n"):
                if not self.isDetailPaneOpen:
                    self.openDetailPane()
                else:
                    self.closeDetailPane()
            # r
            elif key == ord("r"):
                if not self.isDetailPaneOpen:
                    self.__init__(self.window, self.db)
                    return

    def openDetailPane(self):
        self.isDetailPaneOpen = True
        errorId = self.dataList.getSelection()[1]
        details = self.db.fetchErrorDetail(errorId)
        self.detailPane.setData(details)
        self.dataList.shrink()
        self._redraw()

    def closeDetailPane(self):
        self.isDetailPaneOpen = False
        self.dataList.grow()
        self._redraw()


###############################
## OBJECT FOR A LIST OF DATA ##
###############################

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
        width = self.screenCols - 1
        for i in range(startIndex, endIndex):
            if i == self.index:
                colors = curses.color_pair(INVERTED_COLORS)
            else:
                colors = curses.color_pair(REGULAR_COLORS)
            try:
                lineStr = self.items[i]
                lineStr = " " + lineStr[:width].ljust(width, " ")
                self.window.addstr(lineCount, 0, lineStr, colors)
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
        """ Change the screenPos without changing index so there is no whitespace after the last line. """
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


#####################################
## A DETAIL PANE FOR THE DATA LIST ##
#####################################

class DetailPane(object):

    def __init__(self, stdscr):
        screenSize = stdscr.getmaxyx()
        self.screenLines = screenSize[0] - 8
        self.screenCols = screenSize[1]
        self.linePos = 0
        self.colPos = 0
        self.pad = curses.newpad(1, 1)

    def setData(self, data):
        # reset position
        self.linePos = 0
        self.colPos = 0
        # load new data
        data = data.split("\n")
        if isinstance(data, str):
            data = [data]
        self.numLines = len(data)
        self.numCols = 0
        for line in data:
            if len(line) > self.numCols:
                self.numCols = len(line)
        self.pad.clear()
        self.pad.resize(self.numLines, self.numCols)
        for i in range(self.numLines):
            try:
                s = data[i]
                if isHighlightedErrorLine(s):
                    colors = curses.color_pair(ERROR_HIGHLIGHT_COLORS)
                else:
                    colors = curses.color_pair(REGULAR_COLORS)
                self.pad.addstr(i, 0, s, colors)
            except: pass

    def scrollBottom(self):
        self.linePos = self.numLines - self.screenLines
        self.refresh()

    def scrollTop(self):
        self.linePos = 0
        self.refresh()

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
        self.colPos += 5
        if self.colPos + self.screenCols >= self.numCols:
            self.colPos = self.numCols - self.screenCols
        self.refresh()

    def scrollLeft(self):
        self.colPos -= 5
        if self.colPos < 0:
            self.colPos = 0
        self.refresh()

    def scrollPageUp(self):
        self.linePos -= self.screenLines
        if self.linePos < 0:
            self.linePos = 0
        self.refresh()

    def scrollPageDown(self):
        self.linePos += self.screenLines
        if self.linePos + self.screenLines >= self.numLines:
            self.linePos = self.numLines - self.screenLines
        self.refresh()

    def refresh(self):
        self.pad.refresh(self.linePos,self.colPos, 6,0, self.screenLines+5,self.screenCols-1)

