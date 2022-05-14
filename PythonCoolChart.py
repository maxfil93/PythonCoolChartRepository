import math
import sys
from enum import Enum

from PyQt5.QtCore import Qt, qRound, QPoint, QPointF, QRect, QLine, QLineF, QRectF
from PyQt5.QtGui import QBrush, QPen, QFont, QColor, QPixmap, QPainter, QFontMetrics, QPalette, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QSizePolicy


class SeriesType(Enum):
    Line = 0
    Circles = 1


class Series:
    cnt = 0

    pubvar = 0

    def __init__(self, parent):
        self.parent = parent
        self.type = SeriesType.Line
        self.xy = []
        self.xyPix = []
        self.brush = QBrush(Qt.red, Qt.SolidPattern)
        self.pen = QPen(Qt.red, Qt.SolidLine)
        self.id = self.__class__.cnt
        self.__class__.cnt += 1
        self.max_x = self.min_x = self.max_y = self.min_y = 0

        self.visible = True
        self.avg_sum_y = 0
        self.avg_n_y = 0
        self.avg_y = 0
        self.avg_vis_sum_y = 0
        self.avg_vis_n_y = 0
        self.avg_vis_y = 0
        self.name = "Series{}".format(self.id)
        # self.name = 'Series, %s' % id
        self.first_drawable_point_ind = -1
        self.first_drawable_point_x = -1

    def addXY(self, x, y):
        p = QPointF(x, y)
        self.xy.append(p)

        self.avg_sum_y += p.y()
        self.avg_n_y += 1
        self.avg_y = self.avg_sum_y / self.avg_n_y

        if len(self.xy) == 1:
            self.max_x = p.x()
            self.min_x = p.x()
            self.max_y = p.y()
            self.min_y = p.y()

        if p.x() > self.max_x:
            self.max_x = p.x()
        if p.x() < self.min_x:
            self.min_x = p.x()
        if p.y() > self.max_y:
            self.max_y = p.y()
        if p.y() < self.min_y:
            self.min_y = p.y()

        if self.parent.getAutoXLimits():
            if self.min_x < self.parent.getXMin():
                self.parent.setXMin(self.min_x)
            if self.max_x > self.parent.getXMax():
                self.parent.setXMax(self.max_x)

        if self.parent.getAutoYLimits():
            if self.min_y < self.parent.getYMin():
                self.parent.setYMin(self.min_y)
            if self.max_y > self.parent.getYMax():
                self.parent.setYMax(self.max_y)
        self.parent.update()

    def clear(self):
        self.avg_sum_y = 0
        self.avg_n_y = 0
        self.avg_y = 0
        self.avg_vis_sum_y = 0
        self.avg_vis_n_y = 0
        self.avg_vis_y = 0

        self.xy.clear()
        self.parent.update()

    def setType(self, _type):
        self.type = _type
        self.parent.update()

    def setBrush(self, brush):
        self.brush = brush
        self.parent.update()

    def setPen(self, pen):
        self.pen = pen
        self.parent.update()

    def getType(self):
        return self.type

    def getBrush(self):
        return self.brush

    def getPen(self):
        return self.pen

    def getID(self):
        return id

    def setVisible(self, v):
        self.visible = v

    def getVisible(self):
        return self.visible

    def getAvgY(self):
        return self.avg_y

    def getName(self):
        return self.name


class CoolChart(QWidget):
    def __init__(self):

        super().__init__()

        self.x_l = 0
        self.y_l = 0
        self.w_l = 0
        self.h_l = 0
        self.x_f = 0
        self.y_f = 0
        self.w_f = 0
        self.h_f = 0

        self.rmb_pr_p_f = QPointF()
        self.zoom_rect = QRect()
        self.img = QPixmap()
        self.zoom_stack = []

        self.crossLineX = 0
        self.crossLineY = 0

        self.antialiased = False
        self.outerRectPen = QPen()
        self.outerRectPen.setColor(Qt.white)
        self.outerRectPen.setWidth(1)
        self.outerRectPen.setCapStyle(Qt.SquareCap)
        self.outerRectPen.setJoinStyle(Qt.MiterJoin)

        self.outerRectBrush = QBrush(Qt.black, Qt.SolidPattern)
        self.marginTop = 20
        self.marginRight = 10
        self.marginBottom = 20
        self.marginLeft = 100

        self.gridPen = QPen()
        self.gridPen.setColor(Qt.white)
        self.gridPen.setWidth(1)
        self.gridPen.setCapStyle(Qt.SquareCap)
        self.gridPen.setJoinStyle(Qt.MiterJoin)
        self.gridPen.setStyle(Qt.DashLine)
        self.gridLineCountX = 5
        self.gridLineCountY = 5

        self.xMin = sys.float_info.max
        self.xMax = -sys.float_info.max
        self.yMin = sys.float_info.max
        self.yMax = -sys.float_info.max

        self.textFont = QFont()
        self.textFont.setFamily('Consolas')
        self.textFont.setPointSize(10)
        self.textColor = QColor(Qt.white)

        # self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        self.series = []

        self.lmb_pressed = False
        self.rmb_pressed = False
        self.mmb_pressed = False

        self.autoXLimit = True
        self.autoYLimit = True

        self.textX_fmt = 'f'
        self.textX_prec = 3
        self.textY_fmt = 'f'
        self.textY_prec = 3

        self.crossPen = QPen()
        self.crossPen.setColor(Qt.red)
        self.crossPen.setWidth(1)
        self.crossPen.setStyle(Qt.DashLine)

        self.draw_inf_enabled = False

        self.zoom_rect_draw_enable = False

        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.zoom_by_wheel_x = False
        self.zoom_by_wheel_y = False

    def setAntialiased(self, antialiased):
        self.antialiased = antialiased
        self.update()

    def setOuterRectPen(self, pen):
        self.outerRectPen = pen
        self.update()

    def setOuterRectBrush(self, brush):
        self.outerRectBrush = brush
        self.update()

    def setGridPen(self, pen):
        self.gridPen = pen
        self.update()

    def setGridLineCountX(self, X):
        self.gridLineCountX = X
        self.update()

    def setGridLineCountY(self, Y):
        self.gridLineCountY = Y
        self.update()

    def setTextFont(self, font):
        self.textFont = font
        self.update()

    def setTextColor(self, cl):
        self.textColor = cl

    def setTextXFormat(self, fmt):
        self.textX_fmt = fmt

    def setTextYFormat(self, fmt):
        self.textY_fmt = fmt

    def setTextXPrecision(self, precision):
        self.textX_prec = precision

    def setTextYPrecision(self, precision):
        self.textY_prec = precision

    def setMarginTop(self, top):
        self.marginTop = top
        self.update()

    def setMarginLeft(self, left):
        self.marginLeft = left
        self.update()

    def setMarginRight(self, right):
        self.marginRight = right
        self.update()

    def setMarginBottom(self, bottom):
        self.marginBottom = bottom
        self.update()

    def setMargins(self, top, left, right, bottom):
        self.marginTop = top
        self.marginLeft = left
        self.marginRight = right
        self.marginBottom = bottom
        self.update()

    def setXMin(self, xMin):
        self.xMin = xMin
        self.update()

    def setXMax(self, xMax):
        self.xMax = xMax
        self.update()

    def setYMin(self, yMin):
        self.yMin = yMin
        self.update()

    def setYMax(self, yMax):
        self.yMax = yMax
        self.update()

    def setLimits(self, xMin, xMax, yMin, yMax):
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.update()

    def setAutoXLimits(self, autoX):
        self.autoXLimit = autoX

    def setAutoYLimits(self, autoY):
        self.autoYLimit = autoY

    def setCrossPen(self, p):
        self.crossPen = p

    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
    # // ------------------------public - Getters - ------------------------------
    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    def getAntialiased(self):
        return self.antialiased

    def getOuterRectPen(self):
        return self.outerRectPen

    def getOuterRectBrush(self):
        return self.outerRectBrush

    def getGridPen(self):
        return self.gridPen

    def getGridLineCountX(self):
        return self.gridLineCountX

    def getGridLineCountY(self):
        return self.gridLineCountY

    def getTextFont(self):
        return self.textFont

    def getTextColor(self):
        return self.textColor

    def getTextXFormat(self):
        return self.textX_fmt

    def getTextYFormat(self):
        return self.textY_fmt

    def getTextXPrecision(self):
        return self.textX_prec

    def getTextYPrecision(self):
        return self.textY_prec

    def getMarginTop(self):
        return self.marginTop

    def getMarginLeft(self):
        return self.marginLeft

    def getMarginRight(self):
        return self.marginRight

    def getMarginBottom(self):
        return self.marginBottom

    def getXMin(self):
        return self.xMin

    def getXMax(self):
        return self.xMax

    def getYMin(self):
        return self.yMin

    def getYMax(self):
        return self.yMax

    def getAutoXLimits(self):
        return self.autoXLimit

    def getAutoYLimits(self):
        return self.autoYLimit

    def getCrossPen(self):
        return self.crossPen

    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
    # // ------------------------public - Functions - ----------------------------
    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    def addSeries(self, s):
        self.series.append(s)
        return s.getID()

    def getSeriesByID(self, _id):
        for s in self.series:
            if s.getID() == _id:
                return s
        return None

    def deleteSeriesById(self, _id):
        cnt = 0
        for s in self.series:
            if s.getID() == _id:
                del s[cnt]
            cnt += 1
        self.update()

    def clear(self):
        self.series.clear()
        if self.autoXLimit:
            self.xMin = sys.float_info.max
            self.xMax = -sys.float_info.max

        if self.autoYLimit:
            self.yMin = sys.float_info.max,
            self.yMax = -sys.float_info.max

        self.update()

    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
    # // ------------------------private - Functions - ---------------------------
    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    def doesPhisycalLineBelongToChart(self, l):
        x1 = l.p1().x()
        y1 = l.p1().y()
        x2 = l.p2().x()
        y2 = l.p2().y()

        if self.do_lines_cross(x1, y1, x2, y2, self.xMin, self.yMax, self.xMax, self.yMax) or \
                self.do_lines_cross(x1, y1, x2, y2, self.xMax, self.yMax, self.xMax, self.yMin) or \
                self.do_lines_cross(x1, y1, x2, y2, self.xMax, self.yMin, self.xMin, self.yMin) or \
                self.do_lines_cross(x1, y1, x2, y2, self.xMin, self.yMin, self.xMin, self.yMax) or \
                ((x1 >= self.xMin) and (x1 <= self.xMax) and (y1 >= self.yMin) and (y1 <= self.yMax)) or \
                ((x2 >= self.xMin) and (x2 <= self.xMax) and (y2 >= self.yMin) and (y2 <= self.yMax)):
            return True
        else:
            return False

    def doesPhisycalPointBelongToChart(self, p):
        if self.xMin < p.x() < self.xMax and self.yMin < p.y() < self.yMax:
            return True
        return False

    def calcPixDist(self, l):
        d = int(math.sqrt(pow(l.dx(), 2) + pow(l.dy(), 2)))
        return d

    def phisycalPointToPix(self, point):
        res = QPoint()
        x = (point.x() - self.xMin) / ((self.xMax - self.xMin) / self.w_f)
        y = (point.y() - self.yMin) / ((self.yMax - self.yMin) / self.h_f)
        res.setX(qRound(x))
        res.setY(qRound(y))
        return res

    def pixPointToPhisycal(self, point):
        res = QPointF()
        x = (point.x() * ((self.xMax - self.xMin) / self.w_f)) + self.xMin
        y = (point.y() * ((self.yMax - self.yMin) / self.h_f)) + self.yMin
        res.setX(x)
        res.setY(y)
        return res

    def findNearestPointByX(self, ser_ind, x):
        mindx = sys.float_info.max
        res = QPointF()
        for po in self.series[ser_ind].xy:
            p = QPointF(po)
            dx = math.fabs(p.x() - x)
            if dx < mindx:
                mindx = dx
                res = p
        return res

    def zoomByRect(self, r):
        (x1, y1, x2, y2) = r.getCoords()
        p1 = QPoint(x1, y1)
        p2 = QPoint(x2, y2)
        f1 = QPointF(self.pixPointToPhisycal(p1))
        f2 = QPointF(self.pixPointToPhisycal(p2))

        self.xMin = f1.x()
        self.xMax = f2.x()
        self.yMin = f2.y()
        self.yMax = f1.y()

    def grabScreenshot(self):
        wr = QRect(self.rect())
        r1 = QPoint(self.mapToGlobal(QPoint(wr.x(), wr.y())))
        r2 = QPoint(self.mapToGlobal(QPoint(wr.x() + wr.width(), wr.y() + wr.height())))
        gwr = QRect(r1, r2)

        t1 = QPoint(r1 + QPoint(self.x_f, self.y_f))
        t2 = QPoint(r1 + QPoint(self.x_f + self.w_f - 1, self.y_f + self.h_f - 1))
        screenRect = QRect(t1, t2)

        desktopPixmap = QPixmap(screenRect.size())
        p = QPainter(desktopPixmap)

        for screen in QApplication.screens():
            p.drawPixmap(screen.geometry().topLeft(),
                         screen.grabWindow(0, t1.x(), t1.y(), screenRect.width(), screenRect.height()))

        return desktopPixmap

    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
    # // --------------------drawing - private - Functions - -----------------------
    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    def drawChartRectangle(self, p):
        p.setPen(self.outerRectPen)
        p.setBrush(self.outerRectBrush)
        p.drawRect(self.x_l, self.y_l, self.w_l, self.h_l)
        p.fillRect(self.x_f, self.y_f, self.w_f, self.h_f, self.outerRectBrush)

    def drawChartGridAndNumbers(self, p):
        self.drawXNumber(p, 0)
        px_w_sector = self.w_f / (self.gridLineCountX + 1)
        for i in range(0, self.gridLineCountX):
            x = px_w_sector * (i + 1)
            p.setPen(self.gridPen)
            p.drawLine(QLine(x, 0, x, self.h_f))
            self.drawXNumber(p, x)
        self.drawXNumber(p, self.w_f)

        self.drawYNumber(p, 0)
        px_h_sector = self.h_f / (self.gridLineCountY + 1)
        for i in range(0, self.gridLineCountY):
            y = px_h_sector * (i + 1)
            p.setPen(self.gridPen)
            p.drawLine(QLine(0, y, self.w_f, y))
            self.drawYNumber(p, y)
        self.drawYNumber(p, self.h_f)

    def drawAllSeries(self, p):
        for i in range(0, len(self.series)):
            self.drawSeries(i, p)

    def drawSeries(self, i, p):
        if not self.series[i].getVisible():
            return
        if self.series[i].getType() == SeriesType.Line:
            self.drawLineSeries(i, p)
        elif self.series[i].getType() == SeriesType.Circles:
            self.drawCircleSeries(i, p)

    def drawLineSeries(self, i, p):
        l = QLine()
        if len(self.series[i].xy) > 1:
            self.series[i].xyPix.clear()
            self.series[i].avg_vis_sum_y = 0
            self.series[i].avg_vis_n_y = 0
            self.series[i].avg_vis_y = 0

            pr = False

            si = 0
            if self.series[i].first_drawable_point_ind != -1:
                if self.xMin >= self.series[i].first_drawable_point_x:
                    si = self.series[i].first_drawable_point_ind
            elif self.series[i].first_drawable_point_ind >= 1:
                si = self.series[i].first_drawable_point_ind
                while True:
                    si -= 1
                    if si >= 1 and self.series[i].xy[si].x() > self.xMin:
                        break

            else:
                si = 0
                self.series[i].first_drawable_point_ind = -1
                self.series[i].first_drawable_point_x = -1

            p.setPen(self.series[i].getPen())

            for j in range(si, len(self.series[i].xy) - 1):
                ph_l = QLineF(self.series[i].xy[j], self.series[i].xy[j + 1])
                if self.series[i].xy[j].x() > self.xMax:
                    break
                if self.doesPhisycalLineBelongToChart(ph_l):
                    if not pr:
                        self.series[i].first_drawable_point_ind = j
                        self.series[i].first_drawable_point_x = self.series[i].xy[j].x()
                        pr = True

                    p1 = self.phisycalPointToPix(self.series[i].xy[j])
                    p2 = self.phisycalPointToPix(self.series[i].xy[j + 1])
                    l.setP1(p1)
                    l.setP2(p2)
                    if self.calcPixDist(l) >= 1:
                        p.drawLine(l)
                        if len(self.series[i].xy) == 0:
                            if self.doesPhisycalPointBelongToChart(self.pixPointToPhisycal(p1)):
                                self.series[i].xyPix.append(p1)
                                self.series[i].avg_vis_sum_y += self.series[i].xy[j].y()
                                self.series[i].avg_vis_n_y += 1
                                self.series[i].avg_vis_y = float(self.series[i].avg_vis_sum_y) / float(
                                    self.series[i].avg_vis_n_y)

                            if self.doesPhisycalPointBelongToChart(self.pixPointToPhisycal(p2)):
                                self.series[i].xyPix().append(p2)
                                self.series[i].avg_vis_sum_y += self.series[i].xy[j + 1].y()
                                self.series[i].avg_vis_n_y += 1
                                self.series[i].avg_vis_y = float(self.series[i].avg_vis_sum_y) / float(
                                    self.series[i].avg_vis_n_y)

                        else:
                            if self.doesPhisycalPointBelongToChart(self.pixPointToPhisycal(p2)):
                                self.series[i].xyPix.append(p2)
                                self.series[i].avg_vis_sum_y += self.series[i].xy[j + 1].y()
                                self.series[i].avg_vis_n_y += 1
                                self.series[i].avg_vis_y = float(self.series[i].avg_vis_sum_y) / float(
                                    self.series[i].avg_vis_n_y)

        elif len(self.series[i].xy) == 1:
            p1 = self.phisycalPointToPix(self.series[i].xy[0])
            p.drawEllipse(p1, self.series[i].getPen().width() / 2, self.series[i].getPen().width() / 2)

    # def drawLineSeries(self, i, p):
    #     p.setPen(self.series[i].getPen())
    #     l = QLine()
    #     if len(self.series[i].xy) > 1:
    #         for j in range(0, len(self.series[i].xy) - 1):
    #             ph_l = QLineF(self.series[i].xy[j], self.series[i].xy[j + 1])
    #             if True:  # DoesPhisycalLineBelongToChart(ph_l)
    #                 p1 = self.phisycalPointToPix(self.series[i].xy[j])
    #                 p2 = self.phisycalPointToPix(self.series[i].xy[j + 1])
    #                 l.setP1(p1)
    #                 l.setP2(p2)
    #                 if self.calcPixDist(l) >= 1:
    #                     p.drawLine(l)
    #
    #     elif len(self.series[i].xy) == 1:
    #         p1 = self.phisycalPointToPix(self.series[i].xy[0])
    #         p.drawEllipse(p1, self.series[i].getPen().width() / 2, self.series[i].getPen().width() / 2)

    def drawCircleSeries(self, i, p):
        ph_p = QPointF()
        p1 = QPoint()
        for j in range(0, len(self.series[i].xy)):
            ph_p = self.series[i].xy[j]
            if self.doesPhisycalPointBelongToChart(ph_p):
                p1 = self.phisycalPointToPix(ph_p)
                p.drawEllipse(p1, self.series[i].getPen().width() / 2, self.series[i].getPen().width() / 2)

    def drawXNumber(self, painter, x):
        painter.setFont(self.textFont)
        painter.setPen(self.textColor)
        xy = self.pixPointToPhisycal(QPoint(x, 0))
        s = '{:.3f}'.format(xy.x())  # QString::number(xy.x(), textX_fmt, textX_prec)
        painter.setFont(self.textFont)
        fm = QFontMetrics(self.textFont)
        fontheight = fm.height()
        fontwidth = fm.horizontalAdvance(s)
        p_txt = QPoint(x - fontwidth / 2, 0 - self.outerRectPen.width() + fontheight + 4)
        painter.scale(1, -1)
        painter.drawText(p_txt, s)
        painter.scale(1, -1)

    def drawYNumber(self, painter, y):
        painter.setFont(self.textFont)
        painter.setPen(self.textColor)
        xy = self.pixPointToPhisycal(QPoint(0, y))
        s = '{:.3f}'.format(xy.y())  # QString::number(xy.y(), textY_fmt, textY_prec)
        painter.setFont(self.textFont)
        fm = QFontMetrics(self.textFont)
        fontheight = fm.height()
        fontwidth = fm.horizontalAdvance(s)
        p_txt = QPoint(-(fontwidth + self.outerRectPen.width() + 4), -(y - fontheight / 2 + 3))
        painter.scale(1, -1)
        painter.drawText(p_txt, s)
        painter.scale(1, -1)

    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
    # // -------------------------------Events - -------------------------------
    # // ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    def paintEvent(self, event):
        Painter = QPainter(self)

        if self.antialiased:
            Painter.setRenderHint(QPainter.Antialiasing, True)

        if self.hasFocus():
            pen = self.outerRectPen
            cl = self.palette().color(QPalette.Active, QPalette.Highlight)
            pen.setColor(cl)
            Painter.setPen(pen)
            Painter.setBrush(Qt.transparent)
            r = self.rect()
            r.setRight(r.right() - pen.width())
            r.setBottom(r.bottom() - pen.width())
            Painter.drawRoundedRect(r, 2, 2)

        # Координаты линий внешнегоквадрата
        self.x_l = self.marginLeft + self.outerRectPen.width() / 2
        self.y_l = self.marginTop + self.outerRectPen.width() / 2
        self.w_l = self.width() - self.marginLeft - self.marginRight - self.outerRectPen.width()
        self.h_l = self.height() - self.marginTop - self.marginBottom - self.outerRectPen.width()

        # Координаты квадрата заполнения
        self.x_f = self.marginLeft + self.outerRectPen.width()
        self.y_f = self.marginTop + self.outerRectPen.width()
        self.w_f = self.width() - self.marginLeft - self.marginRight - self.outerRectPen.width() - self.outerRectPen.width()
        self.h_f = self.height() - self.marginTop - self.marginBottom - self.outerRectPen.width() - self.outerRectPen.width()

        self.drawChartRectangle(Painter)

        Painter.translate(self.x_f, self.y_f + self.h_f)
        Painter.scale(1, -1)

        self.drawChartGridAndNumbers(Painter)

        Painter.setClipRect(0, 0, self.w_f, self.h_f)

        # if not self.lmb_pressed and not self.mmb_pressed:
        self.drawAllSeries(Painter)

        if self.zoom_rect_draw_enable:
            p1 = QPoint(self.zoom_rect.x(), (self.zoom_rect.y()))
            p2 = QPoint(self.zoom_rect.x() + self.zoom_rect.width(), (self.zoom_rect.y() + self.zoom_rect.height()))
            r = QRect(p1, p2)
            p = QPen(Qt.gray)
            p.setStyle(Qt.SolidLine)
            p.setWidth(2)
            Painter.setPen(p)
            Painter.setBrush(Qt.transparent)
            Painter.drawRect(r)

        if self.mmb_pressed:
            # Painter.scale(1, -1)
            # Painter.drawPixmap(0, -self.h_f, self.w_f, self.h_f, self.img, 0, 0, self.img.width(), self.img.height())
            # Painter.scale(1, -1)

            lx = QLine(QPoint(self.crossLineX, 0), QPoint(self.crossLineX, self.h_f))
            ly = QLine(QPoint(0, self.crossLineY), QPoint(self.w_f, self.crossLineY))

            Painter.setPen(self.crossPen)

            br = QBrush(Qt.transparent)
            Painter.setBrush(br)

            Painter.drawLine(lx)
            Painter.drawLine(ly)
            Painter.scale(1, -1)
            pnt = QPoint(self.crossLineX, self.crossLineY)
            pntf = QPointF(self.pixPointToPhisycal(pnt))

            s = '({:.3f}; {:.3f})'.format(pntf.x(),
                                          pntf.y())  # QString s = "(" + QString::number(pntf.x()) + "; " + QString::number(pntf.y()) + ")"

            Painter.drawText(self.crossLineX + 15, - self.crossLineY + 20, s)
            Painter.scale(1, -1)

            p = QPen(self.crossPen.color())
            p.setStyle(Qt.SolidLine)

            for i in range(0, len(self.series)):
                nr = self.findNearestPointByX(i, pntf.x())
                pp = self.phisycalPointToPix(nr)
                p.setColor(self.series[i].getPen().color())
                p.setWidth(2)
                Painter.setPen(p)
                Painter.drawEllipse(pp, self.series[i].getPen().width() * 2, self.series[i].getPen().width() * 2)
                s = '({:.3f}; {:.3f})'.format(nr.x(), nr.y())
                fm = QFontMetrics(self.textFont)
                fontheight = fm.height()
                fontwidth = fm.horizontalAdvance(s)
                (r, g, b, _) = p.color().getRgb()
                Painter.scale(1, -1)
                invcl = QColor(255 - r, 255 - g, 255 - b)
                Painter.fillRect(pp.x() + 15, -pp.y() + 20 - (fontheight - (fontheight / 3)), fontwidth, fontheight,
                                 invcl)
                Painter.drawText(pp.x() + 15, -pp.y() + 20, s)
                Painter.scale(1, -1)

        if self.draw_inf_enabled:
            self.DrawInf(Painter)

        Painter.end()

    def mouseMoveEvent(self, event):
        if self.rmb_pressed:
            tek_p_f = self.pixPointToPhisycal(event.pos())
            dp = QPointF(tek_p_f - self.rmb_pr_p_f)

            self.xMin -= dp.x()
            self.xMax -= dp.x()

            self.yMin += dp.y()
            self.yMax += dp.y()

            self.rmb_pr_p_f = self.pixPointToPhisycal(event.pos())
            self.update()

        if self.lmb_pressed:
            self.zoom_rect_draw_enable = True
            self.zoom_rect = QRect(QPoint(self.zoom_rect.x(), self.zoom_rect.y()),
                                   QPoint(event.pos().x() - self.x_f, self.h_f - (event.pos().y() - self.y_f)))
            self.update()

        if self.mmb_pressed:
            self.crossLineX = event.pos().x() - self.x_f
            self.crossLineY = self.h_f - event.pos().y() + self.y_f
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lmb_pressed = True
            self.zoom_rect.setX(event.pos().x() - self.x_f)
            self.zoom_rect.setY(self.h_f - (event.pos().y() - self.y_f))
            self.img = self.grabScreenshot()
        elif event.button() == Qt.RightButton:
            self.rmb_pressed = True
            self.rmb_pr_p_f = self.pixPointToPhisycal(event.pos())

        elif event.button() == Qt.MiddleButton:
            self.mmb_pressed = True
            self.img = self.grabScreenshot()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            (x1, y1, x2, y2) = self.zoom_rect.getCoords()
            if x1 > x2:
                if self.zoom_stack:
                    r = self.zoom_stack.pop()
                    (x1, y1, x2, y2) = r.getCoords()
                    self.setAutoXLimits(True)
                    self.setAutoYLimits(True)
                    self.setLimits(x1, x2, y1, y2)
                    self.update()
                else:
                    self.setAutoXLimits(True)
                    self.setAutoYLimits(True)

                    xmin = sys.float_info.max
                    ymin = sys.float_info.max
                    xmax = sys.float_info.min
                    ymax = sys.float_info.min

                    for i in range(0, len(self.series)):
                        for j in range(0, len(self.series[i].xy)):
                            x = self.series[i].xy[j].x()
                            y = self.series[i].xy[j].y()
                            if x < xmin:
                                xmin = x
                            if x > xmax:
                                xmax = x
                            if y < ymin:
                                ymin = y
                            if y > ymax:
                                ymax = y
                    self.setXMin(xmin)
                    self.setXMax(xmax)
                    self.setYMin(ymin)
                    self.setYMax(ymax)
                    self.update()

            elif x1 < x2:
                r = QRectF(QPointF(self.xMin, self.yMin), QPointF(self.xMax, self.yMax))
                self.zoom_stack.append(r)
                self.setAutoXLimits(False)
                self.setAutoYLimits(False)
                self.zoomByRect(self.zoom_rect)
                self.update()
        elif event.button() == Qt.RightButton:
            self.rmb_pressed = False
        elif event.button() == Qt.MiddleButton:
            self.mmb_pressed = False
            self.update()
        self.zoom_rect_draw_enable = False
        self.lmb_pressed = False

    def wheelEvent(self, event):
        numDegrees = event.angleDelta().y()
        x = event.pos().x() - self.x_f
        y = self.h_f - (event.pos().y() - self.y_f)
        self.setAutoXLimits(False)
        self.setAutoYLimits(False)
        ph_p = self.pixPointToPhisycal(QPoint(x, y))

        ww = self.xMax - self.xMin
        hh = self.yMax - self.yMin

        scale_factor = 0.9 if numDegrees > 0 else 1.1

        if self.zoom_by_wheel_x and not self.zoom_by_wheel_y:
            self.xMin = ph_p.x() - (ww / 2. * scale_factor)
            self.xMax = ph_p.x() + (ww / 2. * scale_factor)
        elif self.zoom_by_wheel_y and not self.zoom_by_wheel_x:
            self.yMin = ph_p.y() - (hh / 2. * scale_factor)
            self.yMax = ph_p.y() + (hh / 2. * scale_factor)
        elif not self.zoom_by_wheel_y and not self.zoom_by_wheel_x:
            self.xMin = ph_p.x() - (ww / 2. * scale_factor)
            self.xMax = ph_p.x() + (ww / 2. * scale_factor)
            self.yMin = ph_p.y() - (hh / 2. * scale_factor)
            self.yMax = ph_p.y() + (hh / 2. * scale_factor)



        p_c_x = self.x_f + (self.w_f / 2.)
        p_c_y = self.y_f + (self.h_f / 2.)
        glob_p = self.mapToGlobal(QPoint(p_c_x, p_c_y))
        QCursor.setPos(glob_p)
        self.update()

    def DrawInf(self, p):
        pn = QPen()
        pn.setWidth(1)
        pn.setCapStyle(Qt.SquareCap)
        pn.setJoinStyle(Qt.MiterJoin)

        font = p.font()
        font.setPixelSize(10)
        p.setFont(font)

        for i in range(0, len(self.series)):
            avg = self.series[i].getAvgY()
            avg_vis = self.series[i].avg_vis_y
            p.scale(1, -1)
            p_txt = QPoint(5, (-self.h_f + 10) + (font.pixelSize() * i))
            pn.setColor(self.series[i].getPen().color())
            p.setPen(pn)
            p.drawText(p_txt, '{}: avg: {:.3f}; avg_vis: {:.3f}'.format(self.series[i].getName(), avg, avg_vis))
            p.scale(1, -1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.draw_inf_enabled = not self.draw_inf_enabled
            self.update()
        if event.key() == Qt.Key_Control:
            self.zoom_by_wheel_x = True
            self.zoom_by_wheel_y = False
        if event.key() == Qt.Key_Shift:
            self.zoom_by_wheel_x = False
            self.zoom_by_wheel_y = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.zoom_by_wheel_x = False
        if event.key() == Qt.Key_Shift:
            self.zoom_by_wheel_y = False

    def do_lines_cross(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denominator = (y4 - y3) * (x1 - x2) - (x4 - x3) * (y1 - y2)
        if denominator == 0:
            if (x1 * y2 - x2 * y1) * (x4 - x3) - (x3 * y4 - x4 * y3) * (x2 - x1) == 0 and (x1 * y2 - x2 * y1) * (
                    y4 - y3) - (x3 * y4 - x4 * y3) * (y2 - y1) == 0:
                return True
            else:
                return False
        else:
            numerator_a = (x4 - x2) * (y4 - y3) - (x4 - x3) * (y4 - y2)
            numerator_b = (x1 - x2) * (y4 - y2) - (x4 - x2) * (y1 - y2)
            Ua = numerator_a / denominator
            Ub = numerator_b / denominator
            if 0 <= Ua <= 1 and 0 <= Ub <= 1:
                return True
            else:
                return False
