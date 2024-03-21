import os
import os.path as osp
from osgeo import gdal  # 导入gdal模块，用于处理地理数据
import traceback  # 导入traceback模块，用于异常处理
from shutil import copyfile  # 导入copyfile函数，用于复制文件
from PyQt5 import QtWidgets  # PyQt5库中的图形用户界面模块
from PyQt5.QtCore import Qt  # PyQt5库中的核心模块，包含了一些基本的共享功能
from PyQt5.QtGui import QPalette, QColor  # PyQt5库中的图形模块，用于图形处理
from PyQt5.QtWidgets import (  # PyQt5库中的窗口部件模块，包含了创建窗口应用的基本功能
    QMenu, QAction, QFileDialog, QMessageBox, QTableView, QDialog
)
from qgis.core import (  # QGIS核心模块，包含了处理地图和图层的功能
    QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType, QgsVectorLayer, QgsProject,
    QgsVectorFileWriter, QgsWkbTypes, Qgis, QgsFillSymbol, QgsSingleSymbolRenderer,
    QgsVectorLayerCache, QgsMapLayer, QgsRasterLayer, QgsLayerTreeGroup, QgsLayerTreeLayer
)
from qgis.gui import (  # QGIS图形用户界面模块，包含了与图形用户界面相关的类和函数
    QgsLayerTreeViewMenuProvider, QgsLayerTreeView, QgsLayerTreeViewDefaultActions,
    QgsMapCanvas, QgsMessageBar, QgsAttributeTableModel, QgsAttributeTableView,
    QgsAttributeTableFilterModel, QgsGui, QgsAttributeDialog, QgsProjectionSelectionDialog,
    QgsMultiBandColorRendererWidget
)
import traceback  # 异常处理模块
from widgetAndDialog import LayerPropWindowWidgeter  # 导入自定义的窗口部件模块

PROJECT = QgsProject.instance()  # 获取QGIS项目实例

class menuProvider(QgsLayerTreeViewMenuProvider):  # 自定义的图层树视图菜单提供器类
    def __init__(self, mainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layerTreeView: QgsLayerTreeView = mainWindow.layerTreeView  # 设置图层树视图
        self.mapCanvas: QgsMapCanvas = mainWindow.mapCanvas  # 设置地图画布
        self.mainWindows = mainWindow  # 设置主窗口

    def createContextMenu(self) -> QtWidgets.QMenu:
        try:
            menu = QMenu()  # 创建右键菜单
            self.actions: QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()  # 获取默认图层树视图动作
            if not self.layerTreeView.currentIndex().isValid():
                # 如果当前没有选择的图层节点
                # 添加清除图层选项
                actionDeleteAllLayer = QAction('清除图层', menu)
                actionDeleteAllLayer.triggered.connect(lambda: self.deleteAllLayer())
                menu.addAction(actionDeleteAllLayer)

                menu.addAction('展开所有图层', self.layerTreeView.expandAllNodes)  # 添加展开所有图层选项
                menu.addAction('折叠所有图层', self.layerTreeView.collapseAllNodes)  # 添加折叠所有图层选项
                return menu

            if len(self.layerTreeView.selectedLayers()) > 1:
                # 如果选择了多个图层
                # 添加组选项
                self.actionGroupSelected = self.actions.actionGroupSelected()
                menu.addAction(self.actionGroupSelected)

                actionDeleteSelectedLayers = QAction('删除选中图层', menu)
                actionDeleteSelectedLayers.triggered.connect(self.deleteSelectedLayer)
                menu.addAction(actionDeleteSelectedLayers)  # 添加删除选中图层选项

                return menu

            node: QgsLayerTreeNode = self.layerTreeView.currentNode()  # 获取当前节点
            if node:
                if QgsLayerTree.isGroup(node):
                    # 如果当前节点是组节点
                    group: QgsLayerTreeGroup = self.layerTreeView.currentGroupNode()
                    self.actionRenameGroup = self.actions.actionRenameGroupOrLayer(menu)  # 重命名组
                    menu.addAction(self.actionRenameGroup)
                    actionDeleteGroup = QAction('删除组', menu)  # 删除组
                    actionDeleteGroup.triggered.connect(lambda: self.deleteGroup(group))
                    menu.addAction(actionDeleteGroup)
                elif QgsLayerTree.isLayer(node):
                    # 如果当前节点是图层节点
                    self.actionMoveToTop = self.actions.actionMoveToTop(menu)  # 移动到顶部
                    menu.addAction(self.actionMoveToTop)
                    self.actionZoomToLayer = self.actions.actionZoomToLayer(self.mapCanvas, menu)  # 缩放到图层
                    menu.addAction(self.actionZoomToLayer)

                    layer: QgsMapLayer = self.layerTreeView.currentLayer()  # 获取当前图层

                    actionOpenLayerProp = QAction('图层属性', menu)
                    actionOpenLayerProp.triggered.connect(lambda: self.openLayerPropTriggered(layer))  # 打开图层属性
                    menu.addAction(actionOpenLayerProp)

                    actionDeleteLayer = QAction("删除图层", menu)
                    actionDeleteLayer.triggered.connect(lambda: self.deleteLayer(layer))  # 删除图层
                    menu.addAction(actionDeleteLayer)

                return menu

        except:
            print(traceback.format_exc())

    def openLayerPropTriggered(self, layer):
        try:
            self.lp = LayerPropWindowWidgeter(layer, self.mainWindows)  # 打开图层属性窗口
            print(type(self.lp))
            self.lp.show()
        except:
            print(traceback.format_exc())

    def updateRasterLayerRenderer(self, widget, layer):
        # 更新栅格图层的渲染器
        print("change")
        layer.setRenderer(widget.renderer())
        self.mapCanvas.refresh()

    def deleteSelectedLayer(self):
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所选图层？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # 提示用户确认是否删除选定的图层
        if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除所选图层
            layers = self.layerTreeView.selectedLayers()  # 获取所选图层
            for layer in layers:
                self.deleteLayer(layer)  # 调用删除图层的函数

    def deleteAllLayer(self):
        if len(PROJECT.mapLayers().values()) == 0:  # 如果地图层为空
            QMessageBox.about(None, '信息', '您的图层为空')  # 提示图层为空
        else:
            deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所有图层？", QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)  # 提示用户确认是否删除所有图层
            if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除所有图层
                for layer in PROJECT.mapLayers().values():  # 遍历所有地图层
                        self.deleteLayer(layer)  # 调用删除图层的函数

    def deleteGroup(self, group: QgsLayerTreeGroup):
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除组？", QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)  # 提示用户确认是否删除组
        if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除组
            layerTreeLayers  = group.findLayers()  # 查找组中的所有图层
            for layer in layerTreeLayers:
                self.deleteLayer(layer.layer())  # 调用删除图层的函数
        PROJECT.layerTreeRoot().removeChildNode(group)  # 从图层树中移除组节点

    def deleteLayer(self, layer):
        PROJECT.removeMapLayer(layer)  # 从项目中移除图层
        self.mapCanvas.refresh()  # 刷新地图画布
        return 0
