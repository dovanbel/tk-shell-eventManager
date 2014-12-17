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
from PyQt4.QtCore import pyqtSignal
from .ui.dialog import Ui_Dialog

import datetime
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
    


def getIconPath(image):
    return os.sep.join([os.path.dirname(__file__),"icons",image])



class parserWidget(QtGui.QFrame):

    clicked = QtCore.Signal(int, object)
    
    def __init__(self, QTimeFrom = None, QTimeTo = None, QTimeRem = None, QTimeEvery = None, taskList = [] ):
        QtGui.QFrame.__init__(self)
        self.color = ["0","0","0"] 

        self.setObjectName("Box")
        styleButton =" QPushButton { border: none;margin: 0px;padding: 0px;    }"
        styleButton+=" QPushButton:hover{border: 1px solid #00BFFF;}"

        buttonLayout = QtGui.QVBoxLayout()
        toTopButton = QtGui.QPushButton()
        toTopButton.setIcon(QtGui.QIcon(QtGui.QPixmap(getIconPath("up.png"))))
        toTopButton.setStyleSheet(styleButton)
        toTopButton.setIconSize(QtCore.QSize(10,10))
        delButton = QtGui.QPushButton()
        delButton.setIcon(QtGui.QIcon(QtGui.QPixmap(getIconPath("delete.png"))))
        delButton.setStyleSheet(styleButton)
        delButton.setIconSize(QtCore.QSize(10,10))
        toDownButton = QtGui.QPushButton()
        toDownButton.setIcon(QtGui.QIcon(QtGui.QPixmap(getIconPath("down.png"))))
        toDownButton.setStyleSheet(styleButton)
        toDownButton.setIconSize(QtCore.QSize(10,10))
        
        buttonLayout.addWidget(toTopButton)
        buttonLayout.addWidget(delButton)
        buttonLayout.addWidget(toDownButton)

        
        toTopButton.clicked.connect(self.onTopClick)
        delButton.clicked.connect(self.onDelClick)
        toDownButton.clicked.connect(self.onBotClick)
        

        
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
        self.timeAction.timeChanged.connect(self.setTimeInColor)
        
        inactivityLabel1  = QtGui.QLabel("Every")
        self.timeInactivity   = QtGui.QTimeEdit(QTimeEvery)
        inactivityLabel2  = QtGui.QLabel("of inactivity")


        taskLabel        = QtGui.QLabel("for")
        self.taskCombo   = QtGui.QComboBox()
        taskLabel2       = QtGui.QLabel("task(s)")
        self.taskCombo.addItem("all")
        self.taskCombo.addItems(taskList)
        

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
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.setTimeInColor(QTimeRem)

    def onTopClick(self) :
        self.clicked.emit(-1,self)

    def onDelClick(self) :
        self.clicked.emit(0,self)

    def onBotClick(self) :
        self.clicked.emit(1,self)

    def setTimeInColor(self, time1):
        import colorsys
        if time1 == None :
            time1 = QtCore.QTime(0,0,0).toPython()

        in2 = datetime.datetime.combine(datetime.date(1,1,1), QtCore.QTime(0,0,0).toPython()) 
        in1 = datetime.datetime.combine(datetime.date(1,1,1), time1.toPython())  
        valueH  = float(((in1-in2).seconds)/60.0/60.0)
        valueSV = 0.3+ float(((in1-in2).seconds)/60.0/60.0/24.0)/1.42857
        self.color= tuple(i * 255 for i in colorsys.hsv_to_rgb(valueH,valueSV,1.0))
        rgbString = "rgb(%s,%s,%s)"%(self.color)
        self.setStyleSheet("QFrame#Box{border: 1px solid "+rgbString +";}")


    def getRGBToHTMLColor(self):
        """ convert an (R, G, B) tuple to #RRGGBB """

        hexcolor = '#%02x%02x%02x' % self.color
        # that's it! '%02x' means zero-padded, 2-digit hex values
        return hexcolor

    def getDataList(self) :
            
            return [self.timeIn.time().toPython(),
                 self.timeOut.time().toPython(),
                 self.timeAction.time().toPython(),
                 self.timeInactivity.time().toPython(),
                 str(self.taskCombo.currentText()),
                 self.getRGBToHTMLColor()]

class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    taskNameList = []

    def __init__(self):
        """
        Constructor
        """


        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        styleButton =" QPushButton { border: none;margin: 0px;padding: 0px;    }"
        styleButton+=" QPushButton:hover{border: 1px solid #00BFFF;}"


        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        self.addFilterButton = QtGui.QPushButton()
        self.addFilterButton.setIcon(QtGui.QIcon(QtGui.QPixmap(getIconPath("add.png"))))
        self.addFilterButton.setStyleSheet(styleButton)
        self.addFilterButton.setIconSize(QtCore.QSize(15,15))


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
        
        # receive parserWidget 
        self.filterlayout = QtGui.QVBoxLayout()
        layout.addWidget(self.addFilterButton)
        layout.addLayout(self.filterlayout)
        

        layout.addStretch()
        layout.addWidget(self.resultLabel)
        layout.addLayout(processButtonLayout)
        self.setLayout(layout)


        self.connect_widget()

        self.finishConstruct_set_ProjectTaskNameList()

        self.addFilterWidget(QTimeFrom = QtCore.QTime(12,30,0), QTimeTo = QtCore.QTime(14,30,0) , QTimeRem = QtCore.QTime(0,30,0), QTimeEvery = QtCore.QTime(0,50,0) )
        self.addFilterWidget(QTimeFrom = QtCore.QTime(0,0,0),   QTimeTo = QtCore.QTime(23,59,59), QTimeRem = QtCore.QTime(1,30,0), QTimeEvery = QtCore.QTime(0,45,0) )      
        #self.addFilterWidget(QTimeFrom = QtCore.QTime(19,30,0), QTimeTo = QtCore.QTime(22,30,0), QTimeRem = QtCore.QTime(0,30,0), QTimeEvery = QtCore.QTime(0,30,0) )



    def addFilterWidget(self, QTimeFrom = QtCore.QTime(12,30,0), QTimeTo = QtCore.QTime(14,30,0), QTimeRem = QtCore.QTime(0,30,0), QTimeEvery = QtCore.QTime(0,45,0) ):
        filterwidget = parserWidget( QTimeFrom , QTimeTo , QTimeRem, QTimeEvery, self.taskNameList  ) 
        filterwidget.clicked.connect(self.parserWidgetClicked)
        self.filterlayout.addWidget(filterwidget)

    def connect_widget(self):
        self.processButton.clicked.connect(self.parseOnClick)
        self.addFilterButton.clicked.connect(self.addFilterWidget)

    def parserWidgetClicked(self, value, widget) :
        self._app.engine.log_info(str(value))
        indexAt = 0
        newIndex = 0
        if value == 0 :
            widget.setParent(None)
        elif value == -1 :
            indexAt = self.filterlayout.indexOf(widget)
            newIndex = indexAt -1
            if  indexAt==0 :
                return
            self.filterlayout.insertWidget(newIndex,widget)

        elif value ==  1 :
            indexAt = self.filterlayout.indexOf(widget)
            if indexAt+1>self.filterlayout.count():
                return
            newIndex = indexAt +1
            self.filterlayout.insertWidget(newIndex,widget)

         
    def getFilterDataList(self):
        
        dataList = []
        for i in range(self.filterlayout.count()): 
            filterWidget = self.filterlayout.itemAt(i).widget()
            dataList.append(filterWidget.getDataList())

        return tuple(dataList) 
            
    

    def finishConstruct_set_ProjectTaskNameList(self):

        import traceback
        import sys

        try :
            import processor
            reload(processor)
            # progressBar, logLabel, app
            self.taskNameList = processor.preLaunch(self.processProgressBar, self.resultLabel, self._app ) 
        except:
            self._app.engine.log_info(traceback.format_exc())
            self.taskNameList = []

    def parseOnClick(self) :
        
        import traceback
        import sys

        try :
            import processor
            reload(processor)
            processor.launch(self.processProgressBar, self.resultLabel, self.getFilterDataList(), self._app ) 
        except:
            self._app.engine.log_info(traceback.format_exc())

