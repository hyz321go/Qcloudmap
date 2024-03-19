import os  # 导入操作系统模块
import os.path as osp  # 导入操作系统路径模块并重命名为osp
from osgeo import gdal  # 导入GDAL库，用于处理地理空间数据
import traceback  # 导入traceback模块，用于捕获异常并打印堆栈跟踪信息
from shutil import copyfile  # 导入shutil模块的copyfile函数，用于复制文件
from PyQt5 import QtWidgets  # 导入QtWidgets模块
from PyQt5.QtCore import Qt  # 导入Qt模块中的Qt类
from PyQt5.QtGui import QPalette, QColor  # 导入QtGui模块中的QPalette和QColor类
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox, QTableView, QDialog  # 导入QtWidgets模块中的QMenu、QAction、QFileDialog、QMessageBox、QTableView和QDialog类
from qgis.core import (  # 导入QGIS核心模块
    QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType, QgsVectorLayer, QgsProject,
    QgsVectorFileWriter, QgsWkbTypes, Qgis, QgsFillSymbol, QgsSingleSymbolRenderer, QgsVectorLayerCache,
    QgsMapLayer, QgsRasterLayer, QgsLayerTreeGroup, QgsLayerTreeLayer
)
from qgis.gui import (  # 导入QGIS GUI模块
    QgsLayerTreeViewMenuProvider, QgsLayerTreeView, QgsLayerTreeViewDefaultActions, QgsMapCanvas,
    QgsMessageBar, QgsAttributeTableModel, QgsAttributeTableView, QgsAttributeTableFilterModel, QgsGui,
    QgsAttributeDialog, QgsProjectionSelectionDialog, QgsMultiBandColorRendererWidget
)
import traceback  # 导入traceback模块，用于捕获异常并打印堆栈跟踪信息

# 获取当前项目
PROJECT = QgsProject.instance()

# 自定义图层树视图菜单提供者
class menuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self, mainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 调用父类的初始化方法
        self.layerTreeView: QgsLayerTreeView = mainWindow.layerTreeView  # 获取主窗口的图层树视图
        self.mapCanvas: QgsMapCanvas = mainWindow.mapCanvas  # 获取主窗口的地图画布
        self.mainWindows = mainWindow  # 保存主窗口的引用

    # 创建图层树视图的上下文菜单
    def createContextMenu(self) -> QtWidgets.QMenu:
        try:
            menu = QMenu()  # 创建一个菜单对象
            self.actions: QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()  # 获取图层树视图的默认操作

            # 如果没有选中任何图层节点
            if not self.layerTreeView.currentIndex().isValid():
                # 提供清除图层、展开所有图层和折叠所有图层的选项
                actionDeleteAllLayer = QAction('清除图层', menu)  # 创建一个清除图层的动作
                actionDeleteAllLayer.triggered.connect(lambda: self.deleteAllLayer())  # 将动作与删除所有图层的函数连接
                menu.addAction(actionDeleteAllLayer)  # 将动作添加到菜单中

                menu.addAction('展开所有图层', self.layerTreeView.expandAllNodes)  # 添加展开所有图层的选项
                menu.addAction('折叠所有图层', self.layerTreeView.collapseAllNodes)  # 添加折叠所有图层的选项
                return menu  # 返回创建的菜单对象

            # 如果选中了多个图层节点
            if len(self.layerTreeView.selectedLayers()) > 1:
                # 提供添加组和删除选中图层的选项
                self.actionGroupSelected = self.actions.actionGroupSelected()  # 获取选中图层的分组操作
                menu.addAction(self.actionGroupSelected)  # 将分组操作添加到菜单中

                actionDeleteSelectedLayers = QAction('删除选中图层', menu)  # 创建一个删除选中图层的动作
                actionDeleteSelectedLayers.triggered.connect(self.deleteSelectedLayer)  # 将动作与删除选中图层的函数连接
                menu.addAction(actionDeleteSelectedLayers)  # 将动作添加到菜单中

                return menu  # 返回创建的菜单对象

            # 如果选中了单个图层节点
            node: QgsLayerTreeNode = self.layerTreeView.currentNode()  # 获取当前选中的节点
            if node:
                if QgsLayerTree.isGroup(node):  # 如果当前节点是一个组
                    # 提供重命名组和删除组的选项
                    group: QgsLayerTreeGroup = self.layerTreeView.currentGroupNode()  # 获取当前组节点
                    self.actionRenameGroup = self.actions.actionRenameGroupOrLayer(menu)  # 获取重命名组的操作
                    menu.addAction(self.actionRenameGroup)  # 将重命名组的操作添加到菜单中
                    actionDeleteGroup = QAction('删除组', menu)  # 创建一个删除组的动作
                    actionDeleteGroup.triggered.connect(lambda: self.deleteGroup(group))  # 将动作与删除组的函数连接
                    menu.addAction(actionDeleteGroup)  # 将动作添加到菜单中
                elif QgsLayerTree.isLayer(node):  # 如果当前节点是一个图层
                    # 创建将图层移动到顶部的动作
                    self.actionMoveToTop = self.actions.actionMoveToTop(menu)
                    # 将动作添加到右键菜单中
                    menu.addAction(self.actionMoveToTop)
                    # 创建将地图缩放至图层范围的动作
                    self.actionZoomToLayer = self.actions.actionZoomToLayer(self.mapCanvas, menu)
                    # 将动作添加到右键菜单中
                    menu.addAction(self.actionZoomToLayer)
                return menu  # 返回创建的菜单对象

        except:
            print(traceback.format_exc())  # 捕获异常并打印堆栈跟踪信息

    # 更新栅格图层的渲染器
    def updateRasterLayerRenderer(self, widget, layer):
        print("change")  # 打印调试信息
        layer.setRenderer(widget.renderer())  # 设置图层的渲染器
        self.mapCanvas.refresh()  # 刷新地图画布

    # 删除选中图层
    def deleteSelectedLayer(self):
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所选图层？",
                                         QMessageBox.Yes | QMessageBox.No,  # 提示用户确认是否删除选中图层
                                         QMessageBox.No)
        if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除选中图层
            layers = self.layerTreeView.selectedLayers()  # 获取选中的图层列表
            for layer in layers:  # 遍历选中的图层
                self.deleteLayer(layer)  # 调用删除图层的函数

    # 删除所有图层
    def deleteAllLayer(self):
        if len(PROJECT.mapLayers().values()) == 0:  # 如果项目中没有图层
            QMessageBox.about(None, '信息', '您的图层为空')  # 显示消息框提示图层为空
        else:
            deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所有图层？",
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)  # 提示用户确认是否删除所有图层
            if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除所有图层
                for layer in PROJECT.mapLayers().values():  # 遍历项目中的所有图层
                    self.deleteLayer(layer)  # 调用删除图层的函数

    # 删除组及其包含的图层
    def deleteGroup(self, group: QgsLayerTreeGroup):
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除组？", QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)  # 提示用户确认是否删除组
        if deleteRes == QMessageBox.Yes:  # 如果用户确认要删除组
            layerTreeLayers = group.findLayers()  # 获取组中的所有图层
            for layer in layerTreeLayers:  # 遍历组中的所有图层
                self.deleteLayer(layer.layer())  # 调用删除图层的函数
            PROJECT.layerTreeRoot().removeChildNode(group)  # 从图层树中移除组节点

    # 删除图层
    def deleteLayer(self, layer):
        PROJECT.removeMapLayer(layer)  # 从项目中移除图层
        self.mapCanvas.refresh()  # 刷新地图画布
        return 0  # 返回0表示删除成功

