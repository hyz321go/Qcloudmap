from qgis.PyQt import QtCore
from qgis.core import QgsApplication
from PyQt5.QtCore import Qt
import os
import traceback
from mainWindow import MainWindow

if __name__ == '__main__':
    QgsApplication.setPrefixPath('C:/qgis322/apps/qgis-ltr', True)
    QgsApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QgsApplication([], True)

    app.initQgis()

    mainWindow = MainWindow()
    mainWindow.show()
    # tif = r"G:\QGIS\myData\ca_nrc_CGG2013an83.tif"
    # mainWindow.addRasterLayer(tif)
    shp = r"G:\QGIS\myData\naturalearth_lowres.shp"
    mainWindow.addVectorLayer(shp)

    app.exec_()
    app.exitQgis()