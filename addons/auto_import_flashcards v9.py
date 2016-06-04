#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Anki Flashcards Generator

This plug-in help you
import generated flashcards
automatically

author: Long Ly
website: flashcardsgenerator.com
last edited: December 21 2015

V2: Merge Initui Method Into __init__ Object
V4: Fix Bug Note Type, Fix Size Main Window
V3: Check Model Base On Name, Before Importing
V5: Remove Combo Box Languages, Add Read Option From File
V6: Only Copy Necessary Files
V7: Changed File Name To Language.txt, Import Csv And Increase Max Field Size
V8: Add More Languages: France, Vietnamese
V9: Add Chinese Language
"""

import os
import sys
import csv

csv.field_size_limit(sys.maxsize)

from PyQt4 import QtGui
from shutil import copyfile, Error
from os.path import join, exists
from aqt import mw
from aqt.qt import *
from aqt import importing
from aqt.utils import showInfo
from anki.importing import TextImporter, AnkiPackageImporter
from anki.importing.noteimp import NoteImporter

class AutoImportWindows(QtGui.QWidget):
    def __init__(self):
        super(AutoImportWindows, self).__init__()
        self.move(300, 300)
        self.setFixedSize(600, 82)
        self.setWindowTitle('Auto Import Flashcards V9')
        self.setWindowIcon(QtGui.QIcon('anki.png'))

        self.btnBrowse = QtGui.QPushButton('Browse', self)
        self.btnBrowse.setToolTip('Click this button to browse <b>generated flashcards folder</b>')
        self.btnBrowse.resize(self.btnBrowse.sizeHint())
        self.btnBrowse.move(5, 5)
        self.btnBrowse.clicked.connect(self.btnBrowseClicked)

        self.txtPath = QtGui.QLineEdit(self)
        self.txtPath.setGeometry(90, 5, 467, 22)
        self.txtPath.setText("AnkiFlashcards Path")

        self.btnImport = QtGui.QPushButton('Import', self)
        self.btnImport.setToolTip('Click this button to import <b>generated flashcards folder</b>')
        self.btnImport.resize(self.btnImport.sizeHint())
        self.btnImport.move(5, 30)
        self.btnImport.setEnabled(False)
        self.btnImport.clicked.connect(self.btnImportClicked)

        self.txtDeck = QtGui.QLineEdit(self)
        self.txtDeck.setGeometry(90, 30, 467, 22)
        self.txtDeck.setText("Deck Name")

        self.pBar = QtGui.QProgressBar(self)
        self.pBar.setGeometry(5, 56, 587, 22)
        self.pBar.setMinimum(0)
        self.pBar.setMaximum(100)

        self.show()

    def btnBrowseClicked(self):
        global basedir
        basedir = QtGui.QFileDialog.getExistingDirectory(self, 'Select Generated Flashcards Folder')
        self.txtPath.setText(basedir)
        self.btnImport.setEnabled(True)

    def btnImportClicked(self):
        self.pBar.setValue(0)

        srcdir = self.txtPath.text()
        desdir = mw.col.media.dir()
        self.recursiveCopyToAnkiMedia(srcdir, desdir)
        print "Copy media files complete..."

        # import note type and flashcards
        activeOpt = open(basedir + r'\Language.txt', 'r').read().split('\n')
        activeOpt[0] = activeOpt[0].replace('\n', '').replace('\r', '')
        print "activecom[0]: " + activeOpt[0]
        if activeOpt[0] in ["[EN] Vietnamese", "[EN] English", "[EN] Chinese"]:
            filePath = basedir + r'\[EN]singleformABCDEFGHLONGLEE123.apkg'
            noteTypeName = u'[en]singleformABCDEFGHLONGLEE123'
        elif activeOpt[0] in ["[EN] English & Vietnamese", "[EN] Vietnamese & English"]:
            filePath = basedir + r'\[EN]multiformABCDEFGHLONGLEE123.apkg'
            noteTypeName = u'[en]multiformABCDEFGHLONGLEE123'
        elif activeOpt[0] in ["[FR] Vietnamese", "[FR] English"]:
            filePath = basedir + r'\[FR]singleformABCDEFGHLONGLEE123.apkg'
            noteTypeName = u'[fr]singleformABCDEFGHLONGLEE123'
        elif activeOpt[0] in ["[FR] English & Vietnamese", "[FR] Vietnamese & English"]:
            filePath = basedir + r'\[FR]multiformABCDEFGHLONGLEE123.apkg'
            noteTypeName = u'[fr]multiformABCDEFGHLONGLEE123'
        else:
            filePath = basedir + r'\[VN]singleformABCDEFGHLONGLEE123.apkg'
            noteTypeName = u'[vn]singleformABCDEFGHLONGLEE123'

        print "noteTypeName: " + noteTypeName
        allmodels = mw.col.models.allNames()
        if noteTypeName not in allmodels:
            self.createNoteType(noteTypeName, filePath)
        self.pBar.setValue(75)
        print "Create Note Type complete..."

        self.importTextFile(self.txtDeck.text(), noteTypeName, basedir + r'\ankiDeck.csv')
        self.pBar.setValue(100)
        print "Import csv file complete..."

        showInfo("Import Anki Flashcard Complete...")

    def recursiveCopyToAnkiMedia(self, srcdir, desdir):
        global count
        count = 0
        for root, dirs, files in os.walk(str(srcdir)):
            for name in files:
                if count < 35:
                    count += 1
                    self.pBar.setValue(count)
                if name not in ['[EN]multiformABCDEFGHLONGLEE123.apkg', '[EN]singleformABCDEFGHLONGLEE123.apkg', '[FR]multiformABCDEFGHLONGLEE123.apkg', '[FR]singleformABCDEFGHLONGLEE123.apkg', '[VN]singleformABCDEFGHLONGLEE123.apkg', 'ankiDeck.csv', 'Language.txt']:
                    try:
                        copyfile(join(root, name), join(desdir, name))
                        print "Copy file to " + join(desdir, name)
                    except IOError as e:
                        print "I/O error({0}): {1}".format(e.errno, e.strerror) + " [" + name + "]"
                    except Error:
                        print "Existent file..."
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        raise
            for name in dirs:
                self.recursiveCopyToAnkiMedia(join(root, name), str(desdir))

    def createNoteType(self, deckName, filePath):
        api = AnkiPackageImporter(mw.col, filePath)
        api.run()

        # remove deck and notes (note type and deck name is the same)
        did = mw.col.decks.id(deckName)
        mw.col.decks.rem(did, True)

        # update UI
        mw.reset()

    def importTextFile(self, deckName, noteType, filePath):
        # select deck
        did = mw.col.decks.id(deckName)
        mw.col.decks.select(did)

        # set note type for deck
        m = mw.col.models.byName(noteType)
        deck = mw.col.decks.get(did)
        deck['mid'] = m['id']
        mw.col.decks.save(deck)

        # import into the collection
        ti = TextImporter(mw.col, filePath)
        ti.delimiter = "\t"
        ti.importMode = 2
        ti.allowHTML = True
        ti.open()
        ti.updateDelimiter()
        ti.run()

        check = mw.col.decks.id('Default')
        if check is not 1:
            showInfo("""There is no Default deck in your Anki
                        Please recover the Default deck.""")
            mw.col.decks.rem(did, True)
        else:
            cids = mw.col.decks.cids(1)
            did = mw.col.decks.id(deckName)
            mw.col.decks.setDeck(cids, did)

        # update UI
        mw.reset()


def importWindow():
    mw.myWidget = window = AutoImportWindows()
    window.show()


action = QAction("Auto Import Flashcards V9", mw)
mw.connect(action, SIGNAL("triggered()"), importWindow)
mw.form.menuTools.addAction(action)