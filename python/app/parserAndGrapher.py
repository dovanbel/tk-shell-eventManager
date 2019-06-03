from itertools import cycle
from PyQt4.Qt import *
from PyQt4 import QtCore, QtGui
DEFAULT_COLORS = [0x3366cc, 0xdc3912, 0xff9900, 0x109618, 0x990099,
                  0x0099c6, 0xdd4477, 0x66aa00, 0xb82e2e, 0x316395,
                  0x994499, 0x22aa99, 0xaaaa11, 0x6633cc, 0x16d620]




class ExpanderWidget(QtGui.QWidget):
    hided =QtCore.pyqtSignal()
    def __init__(self, text, widget, parent=None):
        super(ExpanderWidget, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        # better use your own icons
        # these are kind of ugly :)
        style = QtGui.QCommonStyle()
        self.rightArrow = style.standardIcon(QtGui.QStyle.SP_ArrowRight)
        self.downArrow = style.standardIcon(QtGui.QStyle.SP_ArrowDown)

        self.toggle = QtGui.QPushButton(self.downArrow, text)
        self.toggle.clicked.connect(self.toggleWidget)

        self.widget = widget

        self.layout.addWidget(self.toggle)
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

    def toggleWidget(self):
        if self.widget.isVisible():
            self.toggle.setIcon(self.rightArrow)
            #self.widget.setVisible(False)
            self.widget.hide()
            self.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)

        else:
            self.toggle.setIcon(self.downArrow)
            self.widget.show()
            #self.widget.setVisible(True)
            self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        self.hided.emit()
class myFolder(QtGui.QWidget):
    hided =QtCore.pyqtSignal()

    def __init__(self, title, widget, parent=None):
        super(myFolder, self).__init__(parent)
        self.widget = widget

        mainLay = QtGui.QVBoxLayout()
        self.setLayout(mainLay)

        self.clickBox = QtGui.QCheckBox(self)
        self.clickBox.setMaximumHeight(20)
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
            self.setSizeHint(20)
        else :
            self.widget.show()
            self.setSizeHint(200)
        self.hided.emit()

class Chart(object):
    def __init__(self, data, colors=None):
        #QPushButton.__init__(self)
        self.data = data
        self.colors = colors

        self._ref_col = 0
        self._ref_isv = True

        self.legendRectList = []
        self.legendRectDraw = []

    def setVerticalAxisColumn(self, column):
        self._ref_col = column
        self._ref_isv = True

    def setHorizontalAxisColumn(self, column):
        self._ref_col = column
        self._ref_isv = False

    def save(self, filename, chart_size, legend_width=None):
        image_size = chart_size
        if legend_width is not None:
            image_size = image_size + QSize(legend_width, 0)

        image = QImage(image_size, QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(image.rect(), Qt.white)
        self.draw(painter, QRect(QPoint(0, 0), chart_size))
        if legend_width is not None:
            self.drawLegend(painter, QRect(QPoint(chart_size.width(), 10), QSize(legend_width, chart_size.height())))
        painter.end()
        return image.save(filename)

    def draw(self, painter, rectangle, test= None):
        raise NotImplementedError


    def getLegend(self, p, _get = False, _switch = False ) :

        idx = 0
        clickedIdx = None

        for  legendRect in self.legendRectList :
            

            if( p.x()>legendRect.x() and p.x()<legendRect.x()+legendRect.width() and p.y()>legendRect.y() and p.y()<legendRect.y()+legendRect.height() ) :
                clickedIdx = idx
                if _switch :
                    self.legendRectDraw[idx] = True

                elif _get :
                    if not self.legendRectDraw[idx] :
                         self.legendRectDraw[idx] = not self.legendRectDraw[idx]
                    return idx
                else :
                    self.legendRectDraw[idx] = not self.legendRectDraw[idx]
            else :
                if _switch : 
                    self.legendRectDraw[idx] = False

            idx += 1

        return [ clickedIdx, self.legendRectDraw ]


    def drawLegend(self, painter, rectangle):

        SPACE = 1

        font_metrics = painter.fontMetrics()
        size = font_metrics.xHeight() * 3


        y = SPACE
        x0 = SPACE
        x1 = x0 + size + SPACE * 3

        w = rectangle.width() - size - SPACE
        tw = w - x1

        painter.save()
        painter.translate(rectangle.x(), rectangle.y())

        color = self._icolors()
        self.legendRectList = []

        if not len(self.legendRectDraw):
            for t,r in enumerate(self._fetchLegendData()) :
                self.legendRectDraw.append(True)

        for i, column in enumerate(self._fetchLegendData()):
            if (y + size + SPACE * 2) >= (rectangle.y() + rectangle.height()) and i < (len(self.data.columns) - 1):
                painter.drawText(x1, y, tw, size, Qt.AlignLeft | Qt.AlignVCenter, "...")
                y += size + SPACE
                break

            text = font_metrics.elidedText(column, Qt.ElideRight, tw)

            if self.legendRectDraw[i] :
                painter.fillRect(x0, y, size, size, QColor(next(color)))
                painter.drawText(x1, y, tw, size, Qt.AlignLeft | Qt.AlignVCenter, text)
            else :
                next(color)
                painter.fillRect(x0, y, size, size, QColor(0,0,0) )
                painter.drawText(x1, y, tw, size, Qt.AlignLeft | Qt.AlignVCenter, text)

            self.legendRectList.append(QRect(x0,y, size,size ) )
            
            y += size + SPACE

        painter.setPen(Qt.lightGray)
        painter.drawRect(0, 0, w, y)
        painter.restore()
        return self.legendRectDraw

    def _fetchLegendData(self):
        for i, column in enumerate(self.data.columns):
            if i != self._ref_col:
                yield column

    def _icolors(self):
        if self.colors is None:
            return cycle(DEFAULT_COLORS)
        return cycle(self.colors)

class PieChart(Chart):
    def draw(self, painter, rectangle, test = None):
        painter.save()
        painter.translate(rectangle.x(), rectangle.y())

        # Calculate Values
        vtotal = float(sum(row[not self._ref_col] for row in self.data.rows))
        values = [row[not self._ref_col] / vtotal for row in self.data.rows]

        # Draw Char
        start_angle = 90 * 16
        for color, v in zip(self._icolors(), values):
            span_angle = v * -360.0 * 16
            painter.setPen(Qt.white)
            painter.setBrush(QColor(color))
            painter.drawPie(rectangle, start_angle, span_angle)
            start_angle += span_angle

        painter.restore()

    def _fetchLegendData(self):
        for row in self.data.rows:
            yield row[self._ref_col]

class ScatterChart(Chart):
    SPAN = 10

    def __init__(self, data, **kwargs):
        super(ScatterChart, self).__init__(data, **kwargs)

        self.haxis_title = None
        self.haxis_vmin = None
        self.haxis_vmax = None
        self.haxis_step = None
        self.haxis_grid = True

        self.vaxis_title = None
        self.vaxis_vmin = None
        self.vaxis_vmax = None
        self.vaxis_step = None
        self.vaxis_grid = True

    def draw(self, painter, rectangle , legendDrawList = None):

        self._setupDefaultValues()

        font_metrics = painter.fontMetrics()
        h = font_metrics.xHeight() * 2
        x = font_metrics.width(self._vToString(self.vaxis_vmax))

        # Calculate X steps
        #print self.vaxis_vmax, self.vaxis_vmin,  self.vaxis_step
        nxstep = int(round((self.haxis_vmax - self.haxis_vmin) / self.haxis_step))
        nystep = int(round((self.vaxis_vmax - self.vaxis_vmin) / self.vaxis_step))
        
        # Calculate chart space
        xmin = h + self.SPAN + x
        xstep = (rectangle.width() - xmin - (h + self.SPAN)) / nxstep
        xmax = xmin + xstep * nxstep
        xmin = 50
        # Calculate Y steps
        ymin = h + self.SPAN

        ystep = (rectangle.height() - ymin - (h * 2 + self.SPAN)) / float( nystep )
        
        ymax = ymin + ystep * nystep

        painter.save()
        painter.translate(rectangle.x(), rectangle.y())

        # Draw Axis Titles
        painter.save()
        self._drawAxisTitles(painter, xmin, xmax, ymin, ymax)
        painter.restore()

        # Draw Axis Labels
        painter.save()
        self._drawAxisLabels(painter, xmin, xmax, ymin, ymax, xstep, nxstep, ystep, nystep)
        painter.restore()

        # Draw Data
        painter.save()
        painter.setClipRect(xmin + 1, ymin, xmax - xmin - 2, ymax - ymin - 1)
        self._drawData(painter, xmin, xmax, ymin, ymax, legendDrawList)
        painter.restore()

        # Draw Border
        painter.setPen(Qt.black)
        painter.drawLine(xmin, ymin, xmin, ymax)
        painter.drawLine(xmin, ymax, xmax, ymax)
  
        painter.restore()

    def _drawAxisTitles(self, painter, xmin, xmax, ymin, ymax):

        font_metrics = painter.fontMetrics()
        h = font_metrics.xHeight() * 2
        hspan = self.SPAN / 2

        font = painter.font()
        font.setItalic(True)
        painter.setFont(font)

        if self.haxis_title is not None:
            painter.drawText(xmin + ((xmax - xmin) / 2 - font_metrics.width(self.haxis_title) / 2), ymax + h * 2 + hspan, self.haxis_title)

        if self.vaxis_title is not None:
            painter.rotate(90)
            painter.drawText(ymin + (ymax - ymin) / 2 - font_metrics.width(self.vaxis_title) / 2, -hspan, self.vaxis_title)

    def _drawAxisLabels(self, painter, xmin, xmax, ymin, ymax, xstep, nxstep, ystep, nystep):
    
        font_metrics = painter.fontMetrics()
        h = font_metrics.xHeight() * 2

        # Draw Internal Grid

        painter.setPen(Qt.lightGray)
        x = xmin + xstep
        ys = ymin if self.haxis_grid else ymax - 4
        for _ in xrange(nxstep):
            painter.drawLine(x, ys, x, ymax)
            x += xstep

        y = ymin
        xe = xmax if self.vaxis_grid else xmin + 4
        for _ in xrange(nystep):
            painter.drawLine(xmin, y, xe, y)
            y += ystep

        # Draw Axis Labels
        painter.setPen(Qt.black)
        for i in xrange(1 + nxstep):
            x = xmin + (i * xstep)
            v = self._hToString(self.haxis_vmin + i * self.haxis_step)
            painter.drawText(x - font_metrics.width(v) / 2, 2 + ymax + h, v)

        for i in xrange(1 + nystep):
            y = ymin + (i * ystep)
            v = self._vToString(self.vaxis_vmin + (nystep - i) * self.vaxis_step)
            painter.drawText(xmin - font_metrics.width(v) - 2, y, v)

    def _drawData(self, painter, xmin, xmax, ymin, ymax, legendDrawList = None ):


        c = 0
        color = self._icolors()
        while c < len(self.data.columns):
            if c != self._ref_col:
                if self._ref_isv:
                    a, b = c, self._ref_col
                else:
                    a, b = self._ref_col, c

                #self._drawColumnData(painter, next(color), a, b, xmin, xmax, ymin, ymax, legendDrawList )
                try :
                    if legendDrawList[b-1] :
                        self._drawColumnData(painter, next(color), a, b, xmin, xmax, ymin, ymax, legendDrawList )
                    else :
                         next(color)
                except : 
                    self._drawColumnData(painter, next(color), a, b, xmin, xmax, ymin, ymax, legendDrawList )
               
            c += 1

    def _drawColumnData(self, painter, color, xcol, ycol, xmin, xmax, ymin, ymax,  legendDrawList = None ):

        painter.setPen(QPen(QColor(color), 7, Qt.SolidLine, Qt.RoundCap))
        idx = 0
        for row in self.data.rows:
            if legendDrawList[idx] :
                x, y = self._xyFromData(row[xcol], row[ycol], xmin, xmax, ymin, ymax)
                painter.drawPoint(x, y)
        
            idx+=1

    def _xyFromData(self, xdata, ydata, xmin, xmax, ymin, ymax):
        x = xmin + (float(xdata - self.haxis_vmin) / (self.haxis_vmax - self.haxis_vmin)) * (xmax - xmin)
        y = ymin + (1.0 - (float(ydata - self.vaxis_vmin) / (self.vaxis_vmax - self.vaxis_vmin))) * (ymax - ymin)
        return x, y

    def _vToString(self, value):
        if isinstance(self.vaxis_step, float):
            return '%.2f' % value
        if isinstance(self.vaxis_step, int):
            return '%d' % value
        return '%s' % value

    def _hToString(self, value):
        if isinstance(self.haxis_step, float):
            return '%.2f' % value
        if isinstance(self.haxis_step, int):
            return '%d' % value
        return '%s' % value

    def _setupDefaultValues(self):
        def _minMaxDelta(col):
            vmin = None
            vmax = None
            vdelta = 0
            ndelta = 1

            last_value = self.data.rows[0][col]
            vmin = vmax = last_value
            for row in self.data.rows[1:]:
                vdelta += abs(row[col] - last_value)
                ndelta += 1
                if row[col] > vmax:
                    vmax = row[col]
                elif row[col] < vmin:
                    vmin = row[col]

            return vmin, vmax, vdelta / ndelta

        ref_min, ref_max, ref_step = _minMaxDelta(self._ref_col)
        oth_min = oth_max = oth_step = None
        for col in xrange(len(self.data.columns)):
            if col == self._ref_col:
                continue

            cmin, cmax, cstep = _minMaxDelta(col)
            oth_min = cmin if oth_min is None else min(cmin, oth_min)
            oth_max = cmax if oth_max is None else max(cmax, oth_max)
            oth_step = cstep if oth_step is None else (oth_step + cstep) / 2

        if self._ref_isv:
            if self.vaxis_vmin is None: self.vaxis_vmin = ref_min
            if self.vaxis_vmax is None: self.vaxis_vmax = ref_max
            if self.vaxis_step is None: self.vaxis_step = ref_step
            if self.haxis_vmin is None: self.haxis_vmin = oth_min
            if self.haxis_vmax is None: self.haxis_vmax = oth_max
            if self.haxis_step is None: self.haxis_step = oth_step
        else:
            if self.haxis_vmin is None: self.haxis_vmin = ref_min
            if self.haxis_vmax is None: self.haxis_vmax = ref_max
            if self.haxis_step is None: self.haxis_step = ref_step
            if self.vaxis_vmin is None: self.vaxis_vmin = oth_min
            if self.vaxis_vmax is None: self.vaxis_vmax = oth_max
            if self.vaxis_step is None: self.vaxis_step = oth_step

class LineChart(ScatterChart):
    def _drawColumnData(self, painter, color, xcol, ycol, xmin, xmax, ymin, ymax, legendDrawList = None ):
        painter.setPen(QPen(QColor(color), 2, Qt.SolidLine, Qt.RoundCap))


        path = QPainterPath()

        row = self.data.rows[0]
        x, y = self._xyFromData(row[xcol], row[ycol], xmin, xmax, ymin, ymax)
        path.moveTo(x, y)
        idx = 0
        for row in self.data.rows[1:]:
            if legendDrawList[idx ] :
                x, y = self._xyFromData(row[xcol], row[ycol], xmin, xmax, ymin, ymax)
                path.lineTo(x, y)
                painter.drawPath(path)

            idx+=1
class AreaChart(ScatterChart):
    def _drawColumnData(self, painter, color, xcol, ycol, xmin, xmax, ymin, ymax, legendDrawList = None):
        painter.setPen(QPen(QColor(color), 2, Qt.SolidLine, Qt.RoundCap))

        color = QColor(color)
        color.setAlpha(40)
        painter.setBrush(color)

        path = QPainterPath()
        path.moveTo(xmin, ymax)


        for row in self.data.rows:

                x, y = self._xyFromData(row[xcol], row[ycol], xmin, xmax, ymin, ymax)
                path.lineTo(x, y)
            

        path.lineTo(xmax, ymax)
        path.moveTo(xmin, ymax)
        painter.drawPath(path)

class Viewer(QWidget):

    legendClicked = pyqtSignal(object)
    selectionChanged = pyqtSignal(object)

    def __init__(self):
        QWidget.__init__(self)
        self.graph = None


    def mousePressEvent(self, event):

        if event.button() == 2:
            p = event.pos()
            new_p = QPoint( p.x()-self.contentsRect().width()+120, p.y()-20 )
            getLegendIdxList =  self.graph.getLegend( new_p )

            self.selectionChanged.emit( getLegendIdxList[1] )
            if not getLegendIdxList[0] == None:
                self.legendClicked.emit(getLegendIdxList[0]+1)
            self.repaint()
       
        elif event.button() == 1 :
            p = event.pos()
            new_p = QPoint( p.x()-self.contentsRect().width()+120, p.y()-20 )
            getLegendIdx =  self.graph.getLegend( new_p, _get = True )
            if not getLegendIdx == None:
                self.legendClicked.emit(getLegendIdx+1)
            self.repaint()
        else :
            p = event.pos()
            new_p = QPoint( p.x()-self.contentsRect().width()+120, p.y()-20 )
            getLegendIdxList =  self.graph.getLegend( new_p, _switch = True ,_get = False )
 

            self.selectionChanged.emit( getLegendIdxList[1] )
            if not getLegendIdxList[0] == None:
                self.legendClicked.emit(getLegendIdxList[0]+1)
            self.repaint()

        #print self.contentsRect()

    def setGraph(self, func):
        self.graph = func
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)


        if self.graph is not None:
            legendDrawList = self.graph.drawLegend(painter, QRect( event.rect().width() - 120, 20, 120, event.rect().height() - 20))

            self.graph.draw(painter, QRect(0, 0, event.rect().width() - 120, event.rect().height()), legendDrawList )
            

        painter.end()

class DialogViewer(QDialog):
    legendClicked = pyqtSignal(object)
    selectionChanged = pyqtSignal(object)
    def __init__(self, colList ):
        QDialog.__init__(self)

        self.colList = colList

        self.viewer = Viewer()
        self.viewer.legendClicked.connect( self.getColName )
        self.viewer.selectionChanged.connect ( self.getColNameList )
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.viewer)

    def getColName(self, idx) :
        self.legendClicked.emit( self.colList[idx] )

    def getColNameList(self, checkList) :
        selectionColumnNameList = []

     
        for idx in  range( len(self.colList) - 1):
            if checkList[idx] :
                selectionColumnNameList.append(self.colList[idx+1] )

        self.selectionChanged.emit( selectionColumnNameList )

        """
        except :
            pass
        """
    def setGraph(self, func):
        self.viewer.setGraph(func)

class DataTable(object):
    def __init__(self):
        self.columns = []
        self.rows = []

    def addColumn(self, label):
        self.columns.append(label)

    def addRow(self, row):
        assert len(row) == len(self.columns)
        self.rows.append(row)

def _pieChartDemo():
    table = DataTable()
    table.addColumn('Lang')
    table.addColumn('Rating')
    table.addRow(['Java', 17.874])
    table.addRow(['C', 17.322])
    table.addRow(['C++', 8.084])
    table.addRow(['C#', 7.319])
    table.addRow(['PHP', 6.096])

    chart = PieChart(table)
    #chart.save('pie.png', QSize(240, 240), 100)

    view = DialogViewer()
    view.setGraph(chart)
    view.resize(360, 240)
    view.exec_()

def _scatterChartDemo():
    table = DataTable()
    table.addColumn('Quality')
    table.addColumn('Test 1')
    table.addColumn('Test 2')
    table.addRow([ 92,  4.9,  8.0])
    table.addRow([ 94,  2.0,  2.5])
    table.addRow([ 96,  7.2,  6.9])
    table.addRow([ 98,  3.5,  1.2])
    table.addRow([100,  8.0,  5.3])
    table.addRow([102, 15.0, 14.2])

    chart = ScatterChart(table)
    chart.haxis_title = 'Process input'
    chart.haxis_vmin = 0
    chart.haxis_vmax = 16
    chart.haxis_step = 2
    chart.vaxis_title = 'Quality'
    chart.vaxis_vmin = 90
    chart.vaxis_vmax = 104
    chart.vaxis_step = 1

    #chart.save('scatter.png', QSize(400, 240), 100)

    view = DialogViewer()
    view.setGraph(chart)
    view.resize(400, 240)
    view.exec_()

def _lineChartDemo():
    table = DataTable()
    table.addColumn('Time')
    table.addColumn('Site 1')
    table.addColumn('Site 2')
    table.addColumn('Site 3')
    table.addRow([ 4.00, 120,   80,  400])
    table.addRow([ 6.00, 270,  850,  320])
    table.addRow([ 8.30,  50, 1200,  280])
    table.addRow([10.15, 320, 1520,  510])
    table.addRow([12.00, 150,  930, 1100])
    table.addRow([18.20,  62, 1100,  240])

    chart = LineChart(table)
    chart.setHorizontalAxisColumn(0)
    chart.haxis_title = 'Time'
    chart.haxis_vmin = 0.0
    chart.haxis_vmax = 20.0
    chart.haxis_step = 2

    #chart.save('line.png', QSize(400, 240), 100)

    view = DialogViewer()
    view.setGraph(chart)
    view.resize(400, 240)
    view.exec_()



def _areaChartDemo2(colList , rawList, title = None, maxHeight = None, vaxis_step = 1000):
    table = DataTable()

    
    my_Hmin = 0.0
    my_Hmax = 0.0
    my_Hstep= 0.0

    divi = 60.0

    txt = ""
    for c in colList :
        table.addColumn(c)
    for r  in rawList :

        table.addRow(r)
        for rawIdx in range(1 , len(r ) ) :
            r[rawIdx] =  r[rawIdx] / 60.0
            if  r[rawIdx]> my_Hmax :
                my_Hmax = r[rawIdx]

             
    print "MAX : ",  my_Hmax 

    chart = AreaChart(table)
    chart.setHorizontalAxisColumn(0)
    if title :
        chart.haxis_title =  title
    else :
        chart.haxis_title = 'Worked hours per days per projects'
    
    chart.haxis_vmin = 0
    chart.haxis_step = 7

    chart.vaxis_vmax = my_Hmax
    chart.vaxis_step = my_Hmax / 10.0

    chart.vaxis_title = "Hours" 
    """
    if maxHeight :
        
    """
    view = DialogViewer( colList )
    view.setGraph(chart)
    #view.repaint()
    #view.resize(400, 240)
     
    
    return view
    
    view.exec_()










def get_my_taskName(sg_name):
                            
    listNames =[{"text" : "Compo", "icon" : "task_compo.png", "values": ["Compositing", "Comp", "Compo"] },
    {"text" : "lighting", "icon" : "task_lit.png" , "values": ["Lighting", "lighting", "Rendering", "Render"]  },
    {"text" : "Anim", "icon" : "task_animation.png", "values": ["Animation","animation","anim", "Anim"]  },
    {"text" : "layout", "icon" : "task_layout.png" , "values": ["Layout", "layout", "Assembly", "LayOut"] },
    {"text" : "Fur", "icon" : "task_fur.png" , "values": ["fur","Fur", "Groom", "groom", "Hair"] },
    {"text" : "Fx",  "icon" : "task_fx.png" , "values": [ "fx", "FX", "Fx", "fX", "Particles", "Simulation", "nCloth", "Rocks" ] },
    {"text" : "Surface", "icon" : "task_surfacing.png" , "values": ["Surface", "Surfacing"] },             
    {"text" : "modeling", "icon" : "task_modelisation.png" , "values": ["Modeling", "Model" , "model", "modeling", "retopo", "wire" ] },
    {"text" : "rigging", "icon" : "task_rig.png" , "values": ["Rig", "rig", "rigging", "Rigging" ] },
    {"text" : "Art", "icon" : "task_art.png" , "values": ["Art","art"] } ] 



    getName = None
    for names in listNames :
        if sg_name in names["values"] :
            getName =  names["text"]
            break

    if not getName :
        print " the task" , sg_name , " is unknow"

    return getName 





def _gt_( myList, sg_name ) :
    idx = 0
    for a in myList :
        if a == get_my_taskName (sg_name)  :
            return idx
        idx+=1


def _gp_ (myList, sg_prjectName ) :

    idx = 0
    for a in myList :
        if a ==  sg_prjectName  :
            return idx
        idx+=1













































def _All(maxHeight = None):

    import glob
    dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not dayDataContextDict.has_key( date ) :
                dayDataContextDict[date] = testDict[date]
            else :

                dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        


        fileObject.close()
    
    minMax = sorted( dayDataContextDict.keys())

    from datetime import date, timedelta as td

    i = minMax[ 0].split("-")
    j = minMax[-1].split("-")
    d1 = date( int(i[0]) , int(i[1]), int(i[2])  )
    d2 = date( int(j[0]) , int(j[1]), int(j[2])  )
    delta = d2 - d1
  
    for i in range(delta.days + 1):
        if not dayDataContextDict.has_key(  str( d1 + td(days=i) ) ) :
            dayDataContextDict[ str(d1 + td(days=i)) ] = 0


    columnList = ["Days" ,"Brut", "Net" , "Filtered"]

    raw = [0,0,0,0]


    dayIdx = 0
    rawList = []
    import copy
    #for DAY,PROJ in  dayDataContextDict.iteritems():

    for DAY in  sorted( dayDataContextDict.keys() ) :
        PROJ = dayDataContextDict[DAY]
        #print DAY, PROJ 

        
        for idx in range(1, 4 ) :
            raw[idx] = 0
        raw[0] = dayIdx+1

        if not PROJ :
            #if dayIdx>112 and dayIdx<126:
                rawList.append(copy.deepcopy( raw ) )
           
        else :

            for projName, TASK in PROJ.iteritems():

                for compName, values in TASK.iteritems() :
                    raw[ 1 ] += float( values["B"] )
                    raw[ 2 ] += float( values["C"] )
                    filtered = 0
                    for t in values["F"] :
                        filtered+= t*-1.0
                    raw[ 3 ] += float( filtered )
            rawList.append(copy.deepcopy( raw ) )
        dayIdx += 1

    
    return _areaChartDemo2(columnList,  rawList , title = "Worked Hours per days for All projects ", maxHeight = maxHeight )





def _AllProjectTasks(dataType, projectNameList = None):




    import glob
    dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :

        foundProject = False
        if projectNameList != None :
            for projName in projectNameList :
                if projName in datafileName :
                    foundProject = True

        if not foundProject and projectNameList != None  :
            continue 


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not dayDataContextDict.has_key( date ) :
                dayDataContextDict[date] = testDict[date]
            else :

                dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        
        fileObject.close()



    import glob
    ALL_dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not ALL_dayDataContextDict.has_key( date ) :
                ALL_dayDataContextDict[date] = testDict[date]
            else :
                ALL_dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        
        fileObject.close()
        
    minMax = sorted( ALL_dayDataContextDict.keys())

    from datetime import date, timedelta as td

    i = minMax[ 0].split("-")
    j = minMax[-1].split("-")
    d1 = date( int(i[0]) , int(i[1]), int(i[2])  )
    d2 = date( int(j[0]) , int(j[1]), int(j[2])  )
    delta = d2 - d1
  
    for i in range(delta.days + 1):
        if not dayDataContextDict.has_key(  str( d1 + td(days=i) ) ) :
            dayDataContextDict[ str(d1 + td(days=i)) ] = 0


    getAllTasks = []
    for DAY,PROJ in  dayDataContextDict.iteritems():
        if not PROJ :
            continue
        for projName, TASK in PROJ.iteritems():
            for compName, values in TASK.iteritems() :
                myTaskName = get_my_taskName(compName)
                if not myTaskName in getAllTasks :
                    getAllTasks.append(myTaskName )


    getAllTasks = sorted(getAllTasks)
    columnList = ["Days"]

    raw = [0]
    for myTasks in getAllTasks :
        columnList.append(myTasks)
        raw.append(0)

    dayIdx = 0
    rawList = []
    import copy
    #for DAY,PROJ in  dayDataContextDict.iteritems():

    for DAY in  sorted( dayDataContextDict.keys() ) :

        PROJ = dayDataContextDict[DAY]
        #print DAY, PROJ 

        for idx in range(1,len(raw)) :
            raw[idx] = 0
        raw[0] = dayIdx+1

        if not PROJ :
            #if dayIdx>112 and dayIdx<126:
                rawList.append(copy.deepcopy( raw ) )
           
        else :

            for projName, TASK in PROJ.iteritems():

                for compName, values in TASK.iteritems() :
                    if dataType == "F" :
                        filtered = 0
                        for t in values["F"] :
                            filtered += t*-1.0
                        raw[ int(_gt_( getAllTasks, compName ) +1 ) ] += float( filtered )
                    else :
                        raw[ int(_gt_( getAllTasks, compName ) +1 ) ] += float( values[ dataType ] )

                    #raw[ int(_gt_( getAllTasks, compName )+1 ) ] += float( values[dataType] )

            rawList.append(copy.deepcopy( raw ) )
        dayIdx += 1

    text = "Brut"
    if dataType == "B" :
        text = "Brut"
    elif dataType == "F" :
        text = "Filtered"
    else :
        text = "Net"
    return _areaChartDemo2(columnList,  rawList, title =  "Worked hours per days per tasks for selected project      ( " + text +" )"  )



def _AllProjectType_perTasks(taskName, projectNameList):


    import glob
    dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :

        foundProject = False
        if projectNameList != None :
            for projName in projectNameList :
                if projName in datafileName :
                    foundProject = True

        if not foundProject and projectNameList != None  :
            continue 


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not dayDataContextDict.has_key( date ) :
                dayDataContextDict[date] = testDict[date]
            else :

                dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        
        fileObject.close()
    



    import glob
    ALL_dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not ALL_dayDataContextDict.has_key( date ) :
                ALL_dayDataContextDict[date] = testDict[date]
            else :
                ALL_dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        
        fileObject.close()
        
    minMax = sorted( ALL_dayDataContextDict.keys())


    from datetime import date, timedelta as td

    i = minMax[ 0].split("-")
    j = minMax[-1].split("-")
    d1 = date( int(i[0]) , int(i[1]), int(i[2])  )
    d2 = date( int(j[0]) , int(j[1]), int(j[2])  )
    delta = d2 - d1
  
    for i in range(delta.days + 1):
        if not dayDataContextDict.has_key(  str( d1 + td(days=i) ) ) :
            dayDataContextDict[ str(d1 + td(days=i)) ] = 0


    columnList = ["Days" ,"Brut", "Net" , "Filtered"]

    raw = [0,0,0,0]


    dayIdx = 0
    rawList = []
    import copy
    #for DAY,PROJ in  dayDataContextDict.iteritems():

    for DAY in  sorted( dayDataContextDict.keys() ) :
        PROJ = dayDataContextDict[DAY]
        #print DAY, PROJ 

        
        for idx in range(1, 4 ) :
            raw[idx] = 0
        raw[0] = dayIdx+1

        if not PROJ :
                rawList.append(copy.deepcopy( raw ) )           
        else :
            for projName, TASK in PROJ.iteritems():
                for compName, values in TASK.iteritems() :
                    if get_my_taskName( compName ) == get_my_taskName( taskName ) :
                        raw[ 1 ] += float( values["B"] )
                        raw[ 2 ] += float( values["C"] )

                        filtered = 0
                        for t in values["F"] :
                            filtered += t*-1.0
                        raw[ 3 ] += float( filtered )
            rawList.append(copy.deepcopy( raw ) )
        dayIdx += 1

    text = " for selected projects "
    if len( projectNameList ) == 1 :
        text = " for "+ projectNameList[0]
    return _areaChartDemo2(columnList,  rawList , title = get_my_taskName(taskName) +" worked Hours per days " + text )






def _AllProject(dataType ):

    import glob
    dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not dayDataContextDict.has_key( date ) :
                dayDataContextDict[date] = testDict[date]
            else :

                dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        


        fileObject.close()
    
    minMax = sorted( dayDataContextDict.keys())

    from datetime import date, timedelta as td

    i = minMax[ 0].split("-")
    j = minMax[-1].split("-")
    d1 = date( int(i[0]) , int(i[1]), int(i[2])  )
    d2 = date( int(j[0]) , int(j[1]), int(j[2])  )
    delta = d2 - d1
  
    for i in range(delta.days + 1):
        if not dayDataContextDict.has_key(  str( d1 + td(days=i) ) ) :
            dayDataContextDict[ str(d1 + td(days=i)) ] = 0


    getAllProject = []
    for DAY,PROJ in  dayDataContextDict.iteritems():
        if not PROJ :
            continue
        for projName, TASK in PROJ.iteritems():
            if not projName in getAllProject :
                getAllProject.append(projName)




    getAllProject = sorted(getAllProject)
    columnList = ["Days"]

    raw = [0]
    for myProject in getAllProject :
        columnList.append(myProject)
        raw.append(0)

    dayIdx = 0
    rawList = []
    import copy

    for DAY in  sorted( dayDataContextDict.keys() ) :
        PROJ = dayDataContextDict[DAY]

 
        for idx in range(1,len(raw)) :
            raw[idx] = 0
        raw[0] = dayIdx+1
        if not PROJ :
                rawList.append(copy.deepcopy( raw ) )
           
        else :
            for projName, TASK in PROJ.iteritems():
                for compName, values in TASK.iteritems() :
                    if dataType == "F" :
                        filtered = 0
                        for t in values["F"] :
                            filtered += t*-1.0
                        raw[ int(_gp_( getAllProject, projName ) +1 ) ] += float( filtered )
                    else :
                        raw[ int(_gp_( getAllProject, projName ) +1 ) ] += float( values[ dataType ] )

            rawList.append(copy.deepcopy( raw ) )
        dayIdx += 1

    text = "Brut "
    if dataType == "B" :
        text = "Brut"
    elif dataType == "F" :
        text = "Filtered"
    else :
        text = "Net "
    return _areaChartDemo2(columnList,  rawList, title = 'Worked hours per days per projects     ('+text+')' )





def _All_tasksPer_Project(projectName, dataType ):

    import glob
    dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*"+projectName+"*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not dayDataContextDict.has_key( date ) :
                dayDataContextDict[date] = testDict[date]
            else :

                dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        

    import glob
    ALL_dayDataContextDict = {}
    for datafileName in glob.glob("C:/temp/EVENTLOG/*.pkl" ) :


        fileObject = open(datafileName,'rb')
        testDict = pickle.load( fileObject )
        for date in  testDict.keys() :
            if not ALL_dayDataContextDict.has_key( date ) :
                ALL_dayDataContextDict[date] = testDict[date]
            else :
                ALL_dayDataContextDict[date][testDict[date].keys()[0]] = testDict[date][ testDict[date].keys()[0] ] 
        
        fileObject.close()
    
    minMax = sorted( ALL_dayDataContextDict.keys())

    from datetime import date, timedelta as td

    i = minMax[ 0].split("-")
    j = minMax[-1].split("-")
    d1 = date( int(i[0]) , int(i[1]), int(i[2])  )
    d2 = date( int(j[0]) , int(j[1]), int(j[2])  )
    delta = d2 - d1
  
 
    for i in range(delta.days + 1):
        if not dayDataContextDict.has_key(  str( d1 + td(days=i) ) ) :
            dayDataContextDict[ str(d1 + td(days=i)) ] = 0


    getAllTasks = []
    for DAY,PROJ in  dayDataContextDict.iteritems():
        if not PROJ :
            continue
        for projName, TASK in PROJ.iteritems():
            for compName, values in TASK.iteritems() :
                myTaskName = get_my_taskName(compName)
                if not myTaskName in getAllTasks :
                    getAllTasks.append(myTaskName )


    getAllTasks = sorted(getAllTasks)
    columnList = ["Days"]

    raw = [0]
    for myTasks in getAllTasks :
        columnList.append(myTasks)
        raw.append(0)

    dayIdx = 0
    rawList = []
    import copy
    #for DAY,PROJ in  dayDataContextDict.iteritems():

    for DAY in  sorted( dayDataContextDict.keys() ) :

        PROJ = dayDataContextDict[DAY]
        #print DAY, PROJ 


        
        for idx in range(1,len(raw)) :
            raw[idx] = 0.0
        raw[0] = dayIdx+1

        if not PROJ :
            #if dayIdx>112 and dayIdx<126:
                rawList.append(copy.deepcopy( raw ) )
           
        else :

            for projName, TASK in PROJ.iteritems():

                for compName, values in TASK.iteritems() :

                    if dataType == "F" :
                        filtered = 0
                        for t in values["F"] :
                            filtered += t*-1.0
                        raw[ int(_gt_( getAllTasks, compName ) +1 ) ] += float( filtered )
                    else :
                        raw[ int(_gt_( getAllTasks, compName ) +1 ) ] += float( values[ dataType ] )

                   #raw[ int(_gt_( getAllTasks, compName )+1 ) ] += float( values[ dataType ] )

            rawList.append(copy.deepcopy( raw ) )
        dayIdx += 1

    text = "Brut "
    if dataType == "B" :
        text = "Brut "
    elif dataType == "F" :
        text = "Filtered "
    else :
        text = "Net "
    return _areaChartDemo2(columnList,  rawList, title =  projectName + " worked hours per days      ( " +  text + " ) ", maxHeight = None,  vaxis_step = 100 )





















class myGraph(QWidget) :
    def __init__(self, parent = None) :
        QWidget.__init__(self, parent )

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.dataType = "B"
        self.selectedProjectList = []

        #y = _All_tasksPer_Project("Alpro Full", 4080)
        w = _All()
        x = _AllProject(dataType = self.dataType )
        y = _AllProjectTasks(dataType = self.dataType )
        #y.exec_()
        
        w.legendClicked.connect( self.redraw_all )
        x.legendClicked.connect( self.drawProjectCalculs )
        x.selectionChanged.connect( self.drawSelectedProjectTasks ) 
        ##y.legendClicked.connect( self.drawSelectedProjectCalculs_types )
        
        folder1 = ExpanderWidget("folder1", w, self)
        folder2 = ExpanderWidget("folder2", x, self)
        folder3 = ExpanderWidget("folder3", y, self)

        self.layout.addWidget(folder1 )
        self.layout.addWidget(folder2 )
        self.layout.addWidget(folder3 )
        self.layout.setAlignment(Qt.AlignTop)
        

        self.layout.addWidget(QLabel("") )
        self.layout.addWidget(QLabel("") )
        
        self.show()


    def redraw_all(self, dataType) :
        if dataType == "Brut" :
            self.dataType = "B"
        elif dataType == "Filtered" :
            self.dataType = "F"
        else :
            self.dataType = "C"


        wid = self.layout.itemAt(1).widget()
        wid.setParent(None)
        wid.deleteLater()

        wid = self.layout.itemAt(1).widget()
        wid.setParent(None)
        wid.deleteLater()

        
        x = _AllProject(dataType = self.dataType )
        y = _AllProjectTasks(dataType = self.dataType )


        
        x.legendClicked.connect( self.drawProjectCalculs )
        x.selectionChanged.connect( self.drawSelectedProjectTasks ) 
        y.legendClicked.connect( self.drawSelectedProjectCalculs_types )

        self.layout.insertWidget(1,x)
        self.layout.insertWidget(2,y)

        wid = self.layout.itemAt(4).widget()
        wid.setParent(None)
        wid.deleteLater()
        self.layout.insertWidget( 4, QLabel())

        wid = self.layout.itemAt(3).widget()
        wid.setParent(None)
        wid.deleteLater()
        self.layout.insertWidget( 3, QLabel())


    def drawSelectedProjectTasks(self, projectList ) :
        wid = self.layout.itemAt(2).widget()
        wid.setParent(None)
        wid.deleteLater()
        self.selectedProjectList = projectList

        y = _AllProjectTasks(dataType = self.dataType,  projectNameList = projectList )
        y.legendClicked.connect( self.drawSelectedProjectCalculs_types )
        self.layout.insertWidget(2,y)


        wid = self.layout.itemAt(4).widget()
        wid.setParent(None)
        wid.deleteLater()
        self.layout.insertWidget( 4, QLabel())

    def drawProjectCalculs(self, projectName) :



        wid = self.layout.itemAt(3).widget()
        
        wid.setParent(None)
        wid.deleteLater()

        z = _All_tasksPer_Project(projectName, self.dataType)
        print projectName
        #z.projectName = projectName
        fct = lambda taskName, project = projectName  :  self.drawOneProjectCalculs_types( taskName, project )
        z.legendClicked.connect( fct )
        self.layout.insertWidget( 3,z)

        wid = self.layout.itemAt(4).widget()
        wid.setParent(None)
        wid.deleteLater()
        self.layout.insertWidget( 4, QLabel())




    def drawOneProjectCalculs_types(self, taskName, project ):
        print taskName
        print project 

        wid = self.layout.itemAt(4).widget()
        wid.setParent(None)
        wid.deleteLater()



        z = _AllProjectType_perTasks(taskName , [project])
        self.layout.insertWidget( 4,z)



    def drawSelectedProjectCalculs_types(self, taskName):


        wid = self.layout.itemAt(4).widget()
        wid.setParent(None)
        wid.deleteLater()

        print self.selectedProjectList 
        z = _AllProjectType_perTasks(taskName, self.selectedProjectList )
        self.layout.insertWidget( 4,z)



if __name__ == '__main__':
    
    import sys, pickle
    app = QApplication(sys.argv)
    #_lineChartDemo()
    #_areaChartDemo()
    #_pieChartDemo()
    #_scatterChartDemo()
    #_lineChartDemo()
    
    #_AllProject()

 
    
    #_All_tasksPer_Project("Alpro Full", 4080)
    

    t = myGraph() 
    t.show()
    sys.exit(app.exec_())
    

    test.exec_()

    




