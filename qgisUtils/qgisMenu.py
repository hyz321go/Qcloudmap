import os
import os.path as osp
from osgeo import gdal  # 导入GDAL库，用于处理栅格数据
import traceback
from shutil import copyfile
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox, QTableView, QDialog
# 从qgis.core导入QGIS的核心库
from qgis.core import (
    QgsLayerTreeNode,
    QgsLayerTree,
    QgsMapLayerType,
    QgsVectorLayer,
    QgsProject,
    QgsVectorFileWriter,
    QgsWkbTypes,
    Qgis,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsVectorLayerCache,
    QgsMapLayer,
    QgsRasterLayer,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer
)
# 导入QGIS的图形用户界面部件
from qgis.gui import (
    QgsLayerTreeViewMenuProvider,
    QgsLayerTreeView,
    QgsLayerTreeViewDefaultActions,
    QgsMapCanvas,
    QgsMessageBar,
    QgsAttributeTableModel,
    QgsAttributeTableView,
    QgsAttributeTableFilterModel,
    QgsGui,
    QgsAttributeDialog,
    QgsProjectionSelectionDialog
)

# 获取当前QGIS项目实例
PROJECT = QgsProject.instance()


# 定义一个名为menuProvider的类，负责提供图层视图的右键菜单
class menuProvider(QgsLayerTreeViewMenuProvider):
    # 初始化方法，mainWindow参数为主窗口
    def __init__(self, mainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layerTreeView: QgsLayerTreeView = mainWindow.layerTreeView  # 主窗口的图层树视图部件
        self.mapCanvas: QgsMapCanvas = mainWindow.mapCanvas  # 主窗口的地图画布
        self.mainWindows = mainWindow  # 保存对主窗口的引用

    # 当用户在图层视图上右键点击时创建并返回一个自定义的上下文菜单
    def createContextMenu(self) -> QtWidgets.QMenu:
        menu = QMenu()  # 创建一个QMenu对象
        self.actions: QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()
        # 当前没有选中的图层，提供的选择有展开/折叠所有图层
        if not self.layerTreeView.currentIndex().isValid():
            menu.addAction('展开所有图层', self.layerTreeView.expandAllNodes)
            menu.addAction('折叠所有图层', self.layerTreeView.collapseAllNodes)
            return menu

        # 选中多个图层时，提供组合和删除菜单项
        if len(self.layerTreeView.selectedLayers()) > 1:
            self.actionGroupSelected = self.actions.actionGroupSelected()  # 添加到组的动作
            menu.addAction(self.actionGroupSelected)

            actionDeleteSelectedLayers = QAction('删除选中图层', menu)  # 创建一个删除图层的动作
            actionDeleteSelectedLayers.triggered.connect(self.deleteSelectedLayer)  # 连接到动作的槽函数
            menu.addAction(actionDeleteSelectedLayers)

            return menu

    # 删除所选图层的方法
    def deleteSelectedLayer(self):
        # 弹出确认删除的消息对话框
        deleteRes = QMessageBox.question(
            self.mainWindows, '信息', "确定要删除所选图层？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if deleteRes == QMessageBox.Yes:
            layers = self.layerTreeView.selectedLayers()  # 获取选中的图层
            for layer in layers:
                # 调用删除图层的方法
                self.deleteLayer(layer)

    # 删除单个图层的方法
    def deleteLayer(self, layer):
        PROJECT.removeMapLayer(layer)  # 从项目中移除图层
        self.mapCanvas.refresh()  # 刷新地图画布
        return 0  # 返回0，表示成功