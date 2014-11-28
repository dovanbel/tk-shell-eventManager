# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog


from datetime import timedelta




def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Parse log events", app_instance, AppDialog)
    




class parserWidget(QtGui.QWidget):
    
    def __init__(self, QTimeFrom = None, QTimeTo = None, QTimeRem = None, QTimeEvery = None, taskList = []):
        QtGui.QWidget.__init__(self)


        mainLayout = QtGui.QHBoxLayout()


        timeLabelLayout = QtGui.QVBoxLayout()
        timeInLabel = QtGui.QLabel("From")
        timeOutLabel = QtGui.QLabel("To")
        
        timeLabelLayout.addWidget(timeInLabel)
        timeLabelLayout.addWidget(timeOutLabel )


        timeInOutLayout = QtGui.QVBoxLayout()
        self.timeIn = QtGui.QTimeEdit(QTimeFrom)
        self.timeOut = QtGui.QTimeEdit(QTimeTo)
        timeInOutLayout.addWidget(self.timeIn)
        timeInOutLayout.addWidget(self.timeOut)

        

        actionLabel     = QtGui.QLabel("Remove")
        self.timeAction = QtGui.QTimeEdit(QTimeRem)

        
        inactivityLabel1  = QtGui.QLabel("Every")
        self.timeInactivity   = QtGui.QTimeEdit(QTimeEvery)
        inactivityLabel2  = QtGui.QLabel("of inactivity")


        taskLabel        = QtGui.QLabel("for")
        self.taskCombo   = QtGui.QComboBox()
        taskLabel2       = QtGui.QLabel("task(s)")
        self.taskCombo.addItems(taskList)
        self.taskCombo.addItem("all")

        mainLayout.addLayout(timeLabelLayout ) 

        mainLayout.addLayout(timeInOutLayout )


        mainLayout.addSpacing(20)
        
        mainLayout.addWidget(actionLabel ) 
        mainLayout.addWidget(self.timeAction ) 
        mainLayout.addSpacing(20)
        
        mainLayout.addWidget(inactivityLabel1 )  
        mainLayout.addWidget(self.timeInactivity )   
        mainLayout.addWidget(inactivityLabel2 )
        mainLayout.addSpacing(20)

        mainLayout.addWidget( taskLabel )   
        mainLayout.addWidget( self.taskCombo )
        mainLayout.addWidget( taskLabel2 )
        mainLayout.addStretch()


        self.setLayout(mainLayout)




class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()



        # logLabel Layout
        self.resultLabel=QtGui.QTextEdit("<font color='#000000'>Results : </font><br><br><br>")

        # main process Button Layout.
        self.processButton = QtGui.QPushButton("Start parsing")

        self.processProgressBar = QtGui.QProgressBar()
        self.processProgressBar.setFormat("waiting somethign to do")
        self.processProgressBar.setTextVisible(True)
        self.processProgressBar.setValue(50)

        processButtonLayout = QtGui.QHBoxLayout()
        processButtonLayout.addWidget(self.processButton)
        processButtonLayout.addWidget(self.processProgressBar)
        #processButtonLayout.addStretch()



        # main layout
        layout = QtGui.QVBoxLayout()

        layout.addWidget(parserWidget(QtCore.QTime(12,30,0) , QtCore.QTime(14,00,0) , QtCore.QTime(0,45,0), QtCore.QTime(1,0,0) ))
        
        layout.addStretch()
        layout.addWidget(self.resultLabel)
        layout.addLayout(processButtonLayout)
        self.setLayout(layout)

        self.connect_widget()



    def connect_widget(self):
        self.processButton.clicked.connect(self.parseOnClick)


    def parseOnClick(self) :
        import traceback

        self.resultLabel.setText("reset")
        try :
            import processor
            reload(processor)
            processor.launch(self.processProgressBar, self.resultLabel,  self._app ) 
        except:

            self._app.engine.log_info(traceback.format_exc()) 

