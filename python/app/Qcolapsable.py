#!/usr/bin/env python

#############################################################################
##
## Copyright (C) 2004-2005 Trolltech AS. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#############################################################################

from PyQt4 import QtCore, QtGui

class myFolder(QtGui.QWidget):
    hided =QtCore.pyqtSignal()

    def __init__(self, title, widget, parent=None):
        super(myFolder, self).__init__(parent)
        self.widget = widget

        mainLay = QtGui.QVBoxLayout()
        self.setLayout(mainLay)

        self.clickBox = QtGui.QCheckBox(self)
        self.clickBox.stateChanged.connect(self.hideWidget)

        barLayout = QtGui.QHBoxLayout()

        barLayout.addWidget(self.clickBox )
        barLayout.addWidget(QtGui.QLabel (title ))
        barLayout.addStretch()
        
        mainLay.addLayout(barLayout)
        mainLay.addWidget(self.widget )


    def hideWidget(self, state):
        if state == 0 :
            self.widget.hide() 
        else :
            self.widget.show()

        self.hided.emit()

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        grid = QtGui.QGridLayout()
        """
        grid.addWidget(self.createFirstExclusiveGroup(), 0, 0)
        grid.addWidget(self.createSecondExclusiveGroup(), 1, 0)
        grid.addWidget(self.createNonExclusiveGroup(), 0, 1)
        """
        fo = myFolder("couco", QtGui.QPushButton("batard de ta race") ,self)
        fo.hided.connect(fo.repaint)
        grid.addWidget(fo, 0, 0)
        grid.addWidget(QtGui.QLabel("bachibouzouk"), 1, 0)
        grid.addWidget(QtGui.QLabel("mil sabord"), 2, 0)
        self.setLayout(grid)

        self.setWindowTitle("Group Box")
        self.resize(480, 320)



if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
