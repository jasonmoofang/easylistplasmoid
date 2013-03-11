#   -*- coding: utf-8 -*-
#
#   Copyright (C) 2009 Petri Damstén <damu@iki.fi>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License as
#   published by the Free Software Foundation; either version 2, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details
#
#   You should have received a copy of the GNU Library General Public
#   License along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os, sys
import requests
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4 import uic
from PyKDE4.plasma import Plasma
from PyKDE4.plasmascript import Applet
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

class Hello(Applet):
    def __init__(self, parent, args = None):
        Applet.__init__(self, parent)
        self.frame = None

    def init(self):
        print '~~~ init'
        self.listname = "default"
        self.username = "<username here>"
        self.password = "<password here>"
        self.serverurl = "http://easylist.willemliu.nl/"
        self.setPopupIcon('korg-todo')
        if not self.extender().hasItem('pyhello'):
            self.extenderItem = Plasma.ExtenderItem(self.extender())
            self.initExtenderItem(self.extenderItem)

    def initExtenderItem(self, item):
        print '~~~ initExtenderItem'
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.listWidget = QListWidget()
        self.connect(self.listWidget, SIGNAL("itemClicked(QListWidgetItem*)"), self.updateList)
        self.proxy = QGraphicsProxyWidget(item)
        self.proxy.setWidget(self.listWidget)
        self.layout.addItem(self.proxy)
        self.listModel = self.config().readEntry(self.listname)

        self.editButton = Plasma.PushButton(item)
        self.editButton.setText("Edit")
        self.layout.addItem(self.editButton)
        self.connect(self.editButton, SIGNAL("clicked()"), self.showEditDialog)

        self.pullButton = Plasma.PushButton(item)
        self.pullButton.setText("Pull")
        self.layout.addItem(self.pullButton)
        self.connect(self.pullButton, SIGNAL("clicked()"), self.doPull)

        self.pushButton = Plasma.PushButton(item)
        self.pushButton.setText("Push")
        self.layout.addItem(self.pushButton)
        self.connect(self.pushButton, SIGNAL("clicked()"), self.doPush)

        self.widget = QGraphicsWidget(item)
        self.widget.setLayout(self.layout)

        item.setWidget(self.widget)
        item.setName('pyhello')
        item.setTitle(i18n('EasyList'))
        item.showCloseButton()
        self.populateList()

    def showEditDialog(self):
        dialog = KDialog()
        dialog.resize(300,200)
        dialog.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
        layout = QVBoxLayout()
        self.editDialogText = QTextEdit(dialog)
        self.editDialogText.setAcceptRichText(False)
        self.editDialogText.insertPlainText(self.listModel)
        layout.addWidget(self.editDialogText)
        main = QWidget(dialog)
        main.setLayout(layout)
        dialog.setMainWidget(main)
        QObject.connect(dialog, SIGNAL("okClicked()"), self.saveEdit)
        dialog.exec_()

    def saveEdit(self):
        self.listModel = self.editDialogText.document().toPlainText()
        print self.listModel
        self.config().writeEntry(self.listname, self.listModel)
        self.config().sync()
        self.populateList()

    def updateList(self, changeditem):
        changeditemtext = changeditem.text()
        changeditemstate = changeditem.checkState()
        thelist = self.listModel.split('\n')
        self.listModel = "";
        if changeditemstate == Qt.Unchecked:
            self.listModel += changeditemtext + "\n"
        for item in thelist:
            if not str(item).strip() == "" and not item == changeditemtext and not str(item).startswith("!"):
                self.listModel += item + "\n"
        if not changeditemstate == Qt.Unchecked:
            self.listModel += "!" + changeditemtext + "\n"
        for item in thelist:
            if not str(item).strip() == "" and not item[1:] == changeditemtext and str(item).startswith("!"):
                self.listModel += item + "\n"
        print self.listModel
        self.config().writeEntry(self.listname, self.listModel)
        self.config().sync()
        self.populateList()

    def populateList(self):
        self.listWidget.clear()
        thelist = self.listModel.split('\n')
        for item in thelist:
            if not str(item).strip() == "" and not str(item).startswith("!"):
                litem = QListWidgetItem(item)
                litem.setFlags(litem.flags() | Qt.ItemIsUserCheckable)
                litem.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(litem)
        for item in thelist:
            if not str(item).strip() == "" and str(item).startswith("!"):
                litem = QListWidgetItem(item[1:])
                litem.setFlags(litem.flags() | Qt.ItemIsUserCheckable)
                litem.setCheckState(Qt.Checked)
                litem.setBackground(QBrush(QColor(255,100,100)))
                self.listWidget.addItem(litem)

    def doPush(self):
        print "pushing: " + self.listModel
        payload = { 'username' : self.username, 'password' : self.password, 'name' : self.listname, 'save' : 'yes plx', 'list' : str(self.listModel) }
        r = requests.post(self.serverurl, data=payload)
        print r.text

    def doPull(self):
        payload = { 'username' : self.username, 'password' : self.password, 'name' : self.listname }
        r = requests.post(self.serverurl, data=payload)
        self.listModel = r.text.split('<textarea id="list" rows="10" cols="50" name="list">')[1].split('</textarea>')[0].replace('\r', '')
        print self.listModel
        self.config().writeEntry(self.listname, self.listModel)
        self.config().sync()
        self.populateList()

def CreateApplet(parent):
    return Hello(parent)

