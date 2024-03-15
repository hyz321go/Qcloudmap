# -*- coding: utf-8 -*-
# author： HXD_XXZX
# IDE： PyCharm
# File ：mainWindow.py
# datetime： 2024/3/15 14:15
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.core import QgsProject
from ui.myWindow import Ui_MainWindow

PROJECT = QgsProject.instance()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)