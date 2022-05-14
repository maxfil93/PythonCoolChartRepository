# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math

from PyQt5 import QtWidgets

from PythonCoolChart import *

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QFrame, QLabel, \
    QSizePolicy


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.lay1 = QVBoxLayout()
        self.widget = QWidget()
        self.chart = CoolChart()
        self.initUI()

    def initUI(self):
        self.setGeometry(50, 50, 1400, 900)
        self.setStyleSheet("QMainWindow {background: 'black';}")

        self.lay1.setAlignment(Qt.AlignTop)
        self.setLayout(self.lay1)
        self.widget.setLayout(self.lay1)
        self.setCentralWidget(self.widget)


        self.chart.setMinimumWidth(500)
        s1 = Series(self.chart)
        s2 = Series(self.chart)
        s1.setPen(QPen(Qt.blue))
        s2.setPen(QPen(Qt.red))
        self.chart.addSeries(s1)
        self.chart.addSeries(s2)
        self.chart.setLimits(0, 10, 0, 10)

        #self.chart.setOuterRectBrush(QBrush(Qt.green))

        for i in range(0, 500):
            s1.addXY(i, math.sin(i*0.1))
            s2.addXY(i, math.cos(i*0.1))
        self.lay1.addWidget(self.chart)

        self.show()


if __name__ == '__main__':


    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

    # print_hi('PyCharm')
    # # Create a new plot
    # figure = pyplot.figure()
    # axes = mplot3d.Axes3D(figure)
    #
    # # Load the STL files and add the vectors to the plot
    # your_mesh = mesh.Mesh.from_file('/home/user/stl_test.stl')
    # axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))
    #
    # # Auto scale to the mesh size
    # scale = your_mesh.points.flatten()
    # axes.auto_scale_xyz(scale, scale, scale)
    #
    # # Show the plot to the screen
    # pyplot.show()


