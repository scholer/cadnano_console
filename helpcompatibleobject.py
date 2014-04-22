#!/usr/bin/env python
# -*- coding: utf-8 -*-
##    Copyright 2011 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
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
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Sat Apr 20 2013

@author: scholer

"""

import os

cadnano_console_path = os.getcwd()
if not "cadnano_console" in cadnano_console_path:
    cadnano_console_path +=  "/plugins/cadnano_console"



class HelpCompatibleObject(object):
    """ Produces a 'help compatible' object, i.e. an object that is self-describing to the user
        from the command line.
        Help items are stored in self.helpitems, as a two-tuple list in the format:
        [(topicheader, bodycontent) for helpitem in self.helpitems]
        
        Topics can either be added by adding text files to a ./help directory,
        or they can be added to self.helpitems manually.
        Note that re-reading the help files with noupdateself=True 
        will cause existing items in self.helpitems to be dropped,
        while running parsehelpfiles with reread=True may cause duplicate
        entries in the helpitems list.
        But, as long as you dont mess with the defaults, the method should function fine.
    """

    def __init__(self):
        self.helpitems = list()
        self.helptxtfilesread = False
        self._helpstr = self.getInitialHelpStr()


    def help(self):
        self.parsehelpfiles()
        print self._helpstr
        helpfmtstr = "------------------\n{0}\n------------------\n{1}"
        print "\n\n".join([helpfmtstr.format(item[0],item[1]) for item in helpitems])

    def parsehelpfiles(self, reread=False, noupdateself=False):
        """
        This is only called when help is requested by the user, so as to not add an unnessecary 
        overhead during initialization.
        If reread is set to True, all help files will be read again.
        """
        print "This is not really implemented yet."
        if self.helptxtfilesread and not reread:
            return
        if noupdateself:
            lst = list()
        else:
            lst = self.helpitems
        import glob
        helpfiles = glob.glob(cadnano_console_path+"/help/*.txt")
        for fp in helpfiles:
            with open(fp, 'Ur') as fh:
                lst.append((fh.name[:-4], fh.read()))
        self.helptxtfilesread = True
        return lst


    def getInitialHelpStr(self):
        helpstr = """
GENERIC HELP OBJECT HELP:

"""
        return helpstr
