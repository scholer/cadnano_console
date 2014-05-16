#!/usr/bin/env python
# -*- coding: utf-8 -*-
##    Copyright 2014 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##
# pylint: disable-msg=C0103,C0301,C0302,R0201,R0902,R0904,R0913,W0142,W0201,W0221,W0402

import os.path, sys
import cadnano, util
util.qtWrapImport('QtGui', globals(), ['QIcon', 'QPixmap', 'QAction'])

from pyinterp import MyInterpreter
#from autobreakconfig import AutobreakConfig
from cadnano_api import CadnanoAPI


class ConsoleHandler(object):
    def __init__(self, document, window):
        self.doc, self.win = document, window
        icon10 = QIcon()
        # Not (!) using qt resources as compiled in ui/mainwindow/icons.qrc.
        # Plugins should be "plugable" and not dependent on re-combiling resources
        # or otherwise re-configuring the exisitng resource hierarchy.
        # PS: If this is not reliable, consider using
        #     icon_path = os.getcwd() + "/plugins/cadnano_console/console_32x32.png"
        icon_path = os.path.join(os.path.dirname(__file__), "console_32x32.png")
        icon10.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.actionOpenConsole = QAction(window)
        self.actionOpenConsole.setIcon(icon10)
        self.actionOpenConsole.setText('Console')
        self.actionOpenConsole.setToolTip("Open cadnano console interface.")
        self.actionOpenConsole.setObjectName("actionOpenConsole")
        self.actionOpenConsole.triggered.connect(self.actionOpenConsoleSlot)
        self.win.menuPlugins.addAction(self.actionOpenConsole)
        # add to main tool bar
        self.win.topToolBar.insertAction(self.win.actionFiltersLabel, self.actionOpenConsole)
        #self.win.topToolBar.insertSeparator(self.win.actionFiltersLabel)
        self.consoleWindow = None
        self.Api = None

    def actionOpenConsoleSlot(self):
        """
        Opens the cadnano2 console.
        Performance: Only load the api when the console is first opened.
        Notice: locals are not updated upon loading a new design. This may cause issues.
        """
        print "cadnano_console.actionOpenConsoleSlot() invoked (DEBUG)"
        if "-i" in sys.argv:
            print "Cadnano was invoked in interactive mode (with '-i' argument) -- opening another console will only cause problems, aborting..."
            return
        # MyInterpreter is the interpreter widget/window.
        win = self.consoleWindow = MyInterpreter(None)
        self.consoleWindow.show()
        # terp (a pyinterp.PyInterp object) is the actual interpreter that is shown
        # by the MyInterpreter widget.
        terp = self.interpreter = self.consoleWindow.textEdit
        # Setting interpreter locals:
        # NOTICE: LOCALS ARE CURRENTLY NOT UPDATED
        # Variables can be made easily accessible for interpreter reference in either of two ways:
        # 1) terp.terp.interpreterLocals['myvar'] = 'some string'
        # 2) terp.updateInterpreterLocals(myvar, "varname")
        # If no second argument is passed then myvar must be referenced as "<classname>_object", e.g.
        # terp.updateInterpreterLocals(app) # app can be refered to with CadnanoQt_object
        # You can import all local variables, either to a dict in the interpreters locals,
        # or populating it with all locals:
        terp.updateInterpreterLocals(locals(), "app_locals")  # locals accessible via app_locals['varname']
        #terp.interpreterLocals.update(locals()) # all locals directly available via varname
        doc = self.doc
        part = self.doc.controller().activePart()
        # Note: Part will be empty if console/interpreter was opened before loading a cadnano file (document).
        app = cadnano.app() # should return the app singleton.
        if not self.Api:
            self.Api = CadnanoAPI()
        api = self.Api
        """ Probably add something at this point?"""

        # Edit: Indeed, adding static objects to the interpreter's locals is not immensely useful,
        # since these might change after the console is opened.
        # Do it the original "interactive" way - adding getter methods, a(), d(), p(), vh(), etc.
        terp.updateInterpreterLocals(api, "api")
        terp.updateInterpreterLocals(doc, "rs_document")
        terp.updateInterpreterLocals(app, "rs_app")
        terp.updateInterpreterLocals(part, "rs_part")
        help_str = """
Cadnano Console - Help:
The cadnano console plugin consists of two parts:
1) A console, which can be used similarly to running cadnano2 in "interactive" mode. (But can be
switched on and off as needed -- I always forget to add the "-i" when starting cadnano ;-)
2) An API which provides console access to some functions and routines that I frequently use.
Unlike the heavily-cluttered part, partItem, etc. which are available in interactive mode,
the API is intended to be clean and easily browsable using dir().

Note: The best way to get acquainted with the interpreter is to view its code in ./plugins/cadnano_console/__init__.py file.

PS: If you did not know that you can run cadnano in "interactive" mode, and
if you have never tried using python's dir() built-in, then this plugin is probably not
for you yet (it is still at a very 'beta' stage of development - my appologies).

All locals (at time of instantiation) are available as app_locals['varname'],
but I will try to update the interpreter's locals to make other
objects easily available as well. In the mean time, use dir() and dir(variable)
to browse around.

Variables can be added to the interpreter's local variables using
PyInterp.updateInterpreterLocals(variable, "variable_name_as_desired").
If no variable_name is given, default is <class name>_object.
The locals can also be accessed directly as PyInterp.interpreterLocals,
while the underlying code.InteractiveInterpreter object can be accessed via PyInterp.interpreter.

Note that MyInterpreter is the window, and PyInterp is the textEdit input/output
that is displayed by MyInterpreter.
PyInterp can also be accessed as MyInterpreter.textEdit.

The api variable has been made to be reliable to use by using functions
instead of static variables, similarly to the functions available in interactive mode;
use them as:
api.doc()
api.filename()
api.active_part()
etc.... Use dir(api) to browse more.

Important note: This interpreter is currently NOT reloaded when you reload a document.
That might cause issues, but should be mitigated if you use api.<function> rather
than the directly stored items.

PS: You can use exit() and quit() to exit the cadnano application.
However, this is NOT graceful; any and all changes will be discarted
without notification.
        """
        def more_help_fun():
            first_help = """
First, know that this is pretty much a python interpreter like the standard.
This means that you can browse the object tree using the dir() command, e.g.
    dir(PyInterp)    to browse the interpreter object.
It also means that you can write
    print <string>
to print a text string. Do this now if you want more help, by typing
    print get_help
            """
            print first_help

        terp.updateInterpreterLocals(help_str, "get_help")
        terp.updateInterpreterLocals(more_help_fun, "more_help")
        terp.write("Welcome to the cadnano2 console plugin!\n")
        terp.write("Use the dir() command to navigate. Use dir(variable) (unquoted) to see a variable's items.\n")
        terp.write("Type more_help() to see more help -- and see how you can invoke a function.\n")
        terp.write("Note: This console should NOT be used if running cadnano in interactive mode (specifying '-i' as argument to main.py).\n")



def documentWindowWasCreatedSlot(doc, win):
    doc.consoleHandler = ConsoleHandler(doc, win)

# Initialization
for c in cadnano.app().documentControllers:
    doc, win = c.document(), c.window()
    doc.consoleHandler = ConsoleHandler(doc, win)
cadnano.app().documentWindowWasCreatedSignal.connect(documentWindowWasCreatedSlot)
