#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

"""
Based in large on old code from github.com/JeffMGreg/PyInterp/
This is a "generic" console; it does not have any cadnano specific
stuff hardcoded; this must be specified on/after object instantiation.

Other entries on this matter:
 -
"""

import os
import re
import sys
import code

try:
    from PySide.QtGui  import *
    from PySide.QtCore import *
except ImportError:
    try:
        from PyQt4.QtGui  import *
        from PyQt4.QtCore import *
    except ImportError:
        print "ImportError: You don't have PySide or PyQt4"
        #sys.exit()


class MyInterpreter(QWidget):

    def __init__(self, parent):

        super(MyInterpreter, self).__init__(parent)
        hBox = QHBoxLayout()

        self.setLayout(hBox)
        self.textEdit = PyInterp(self)

        # this is how you pass in locals to the interpreter
        self.textEdit.initInterpreter(locals())

        self.resize(650, 300)
        self.centerOnScreen()

        hBox.addWidget(self.textEdit)
        hBox.setMargin(0)
        hBox.setSpacing(0)

    def centerOnScreen(self):
        # center the widget on the screen
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width()  / 2) - (self.frameSize().width()  / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

class PyInterp(QTextEdit):

    class InteractiveInterpreter(code.InteractiveInterpreter):
        """ Why is subclassing needed?
        """

        def __init__(self, locals):
            # This doesn't seem like the best way to do this??
            code.InteractiveInterpreter.__init__(self, locals)

        def runIt(self, command):
            # Neither does this:
            code.InteractiveInterpreter.runsource(self, command)


    def __init__(self,  parent):
        super(PyInterp,  self).__init__(parent)

        # And much of this is just fucked:
        sys.stdout              = self
        sys.stderr              = self
        self.refreshMarker      = False # to change back to >>> from ...
        self.multiLine          = False # code spans more than one line
        self.command            = ''    # command to be ran
        self.printBanner()              # print sys info
        self.marker()                   # make the >>> or ... marker
        self.history            = []    # list of commands entered
        self.historyIndex       = -1
        self.interpreterLocals  = {}

        # setting the color for bg and text
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        self.setPalette(palette)
        # This actually seems to be reset at some point?
        # If you want to edit, first do import PyQt4
        # from PyQt4.QtGui import *
        # Then set with PyInterp.setFont(...)
        #self.setFont(QFont('Courier', 10))
        #self.setFont(QFont('Courier New', 8))
        #self.setFont(QFont('Ubuntu Mono', 9))
        self.setFont(QFont('Droid Sans Mono', 8))
        #self.setFont(QFont('Dejavu Sans Mono', 8))

        # initilize interpreter with self locals
        self.initInterpreter(locals())


    def printBanner(self):
        self.write(sys.version)
        self.write(' on ' + sys.platform + '\n')
        self.write('PyQt4 ' + PYQT_VERSION_STR + '\n')
        msg = 'Type !hist for a history view and !hist(n) history index recall'
        self.write(msg + '\n')


    def marker(self):
        if self.multiLine:
            self.insertPlainText('... ')
        else:
            self.insertPlainText('>>> ')

    def initInterpreter(self, interpreterLocals=None):
        if interpreterLocals:
            # when we pass in locals, we don't want it to be named "self"
            # so we rename it with the name of the class that did the passing
            # and reinsert the locals back into the interpreter dictionary
            selfName = interpreterLocals['self'].__class__.__name__
            #print "PyInterp: selfName is {}".format(selfName) # Will be "MyInterpreter"
            interpreterLocalVars = interpreterLocals.pop('self')
            self.interpreterLocals[selfName] = interpreterLocalVars
        else:
            self.interpreterLocals = interpreterLocals
        self.interpreter = self.InteractiveInterpreter(self.interpreterLocals)

    def updateInterpreterLocals(self, newLocals, varname=None):
        """ Original code was stupid, would overwrite definitions.
        e.g. if called with updateInterpreterLocals(locals()), it will overwrite 'dict', meaning
        I can nolonger make new dictionarys !!
        """
        if varname is None:
            varname = newLocals.__class__.__name__
            varname = className + "_object"  # Added by RS to reduce risk of overwriting important names!
        self.interpreterLocals[varname] = newLocals

    def write(self, line):
        self.insertPlainText(line)
        self.ensureCursorVisible()

    def clearCurrentBlock(self):
        # block being current row
        length = len(self.document().lastBlock().text()[4:])
        if length == 0:
            return None
        else:
            # should have a better way of doing this but I can't find it
            [self.textCursor().deletePreviousChar() for x in xrange(length)]
        return True

    def recallHistory(self):
        # used when using the arrow keys to scroll through history
        self.clearCurrentBlock()
        if self.historyIndex <> -1:
            self.insertPlainText(self.history[self.historyIndex])
        return True

    def customCommands(self, command):

        if command == '!hist': # display history
            self.append('') # move down one line
            # vars that are in the command are prefixed with ____CC and deleted
            # once the command is done so they don't show up in dir()
            backup = self.interpreterLocals.copy()
            history = self.history[:]
            history.reverse()
            for i, x in enumerate(history):
                iSize = len(str(i))
                delta = len(str(len(history))) - iSize
                line = line  = ' ' * delta + '%i: %s' % (i, x) + '\n'
                self.write(line)
            self.updateInterpreterLocals(backup)
            self.marker()
            return True

        if re.match('!hist\(\d+\)', command): # recall command from history
            backup = self.interpreterLocals.copy()
            history = self.history[:]
            history.reverse()
            index = int(command[6:-1])
            self.clearCurrentBlock()
            command = history[index]
            if command[-1] == ':':
                self.multiLine = True
            self.write(command)
            self.updateInterpreterLocals(backup)
            return True

        return False

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            # proper exit
            self.interpreter.runIt('exit()')

        if event.key() == Qt.Key_Down:
            if self.historyIndex == len(self.history):
                self.historyIndex -= 1
            try:
                if self.historyIndex > -1:
                    self.historyIndex -= 1
                    self.recallHistory()
                else:
                    self.clearCurrentBlock()
            except:
                pass
            return None

        if event.key() == Qt.Key_Up:
            try:
                if len(self.history) - 1 > self.historyIndex:
                    self.historyIndex += 1
                    self.recallHistory()
                else:
                    self.historyIndex = len(self.history)
            except:
                pass
            return None

        if event.key() == Qt.Key_Home:
            # set cursor to position 4 in current block. 4 because that's where
            # the marker stops
            blockLength = len(self.document().lastBlock().text()[4:])
            lineLength  = len(self.document().toPlainText())
            position = lineLength - blockLength
            textCursor  = self.textCursor()
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)
            return None

        if event.key() in [Qt.Key_Left, Qt.Key_Backspace]:
            # don't allow deletion of marker
            if self.textCursor().positionInBlock() == 4:
                return None

        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            # set cursor to end of line to avoid line splitting
            textCursor = self.textCursor()
            position   = len(self.document().toPlainText())
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)

            line = str(self.document().lastBlock().text())[4:] # remove marker
            line.rstrip()
            self.historyIndex = -1

            if self.customCommands(line):
                return None
            else:
                try:
                    line[-1]
                    self.haveLine = True
                    if line[-1] == ':':
                        self.multiLine = True
                    self.history.insert(0, line)
                except:
                    self.haveLine = False

                if self.haveLine and self.multiLine: # multi line command
                    self.command += line + '\n' # + command and line
                    self.append('') # move down one line
                    self.marker() # handle marker style
                    return None

                if self.haveLine and not self.multiLine: # one line command
                    self.command = line # line is the command
                    self.append('') # move down one line
                    self.interpreter.runIt(self.command)
                    self.command = '' # clear command
                    self.marker() # handle marker style
                    return None

                if self.multiLine and not self.haveLine: #  multi line done
                    self.append('') # move down one line
                    self.interpreter.runIt(self.command)
                    self.command = '' # clear command
                    self.multiLine = False # back to single line
                    self.marker() # handle marker style
                    return None

                if not self.haveLine and not self.multiLine: # just enter
                    self.append('')
                    self.marker()
                    return None
                return None

        # allow all other key events
        super(PyInterp, self).keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyInterpreter(None)
    win.show()
    sys.exit(app.exec_())
