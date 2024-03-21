import traceback  # 导入 traceback 模块，用于打印异常信息
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsStyle, QgsSymbol, QgsWkbTypes, QgsSymbolLayer, QgsFeatureRenderer
from qgis.gui import QgsRendererRasterPropertiesWidget, QgsSingleSymbolRendererWidget, QgsCategorizedSymbolRendererWidget
from PyQt5.QtCore import QModelIndex  # 导入 QModelIndex 类，用于处理模型索引
from ui.layerPropWindow import Ui_LayerProp  # 导入 UI 文件中定义的类
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QTabBar  # 导入 PyQt5 组件类
from qgisUtils import getRasterLayerAttrs, getVectorLayerAttrs  # 导入自定义的函数

PROJECT = QgsProject.instance()  # 获取当前项目实例

class LayerPropWindowWidgeter(QDialog, Ui_LayerProp):
    def __init__(self, layer, parent=None):
        """
        构造函数，初始化图层属性窗口
        :param layer: 要查看属性的图层
        :param parent: 父窗口，默认为 None
        """
        super(LayerPropWindowWidgeter, self).__init__(parent)
        self.layer = layer  # 图层对象
        self.parentWindow = parent  # 父窗口
        self.setupUi(self)  # 设置 UI
        self.initUI()  # 初始化用户界面
        self.connectFunc()  # 连接函数

    def initUI(self):
        """
        初始化用户界面
        """
        layerbar = self.tabWidget.findChild(QTabBar)  # 查找图层选项卡栏
        layerbar.hide()  # 隐藏图层选项卡栏
        renderBar = self.comboTabWidget.findChild(QTabBar)  # 查找渲染选项卡栏
        renderBar.hide()  # 隐藏渲染选项卡栏
        self.listWidget.setCurrentRow(0)  # 设置列表控件当前行为第一行
        self.initInfomationTab()  # 初始化信息选项卡
        self.decideRasterNVector(0)  # 决定是栅格还是矢量图层

    def connectFunc(self):
        """
        连接信号和槽函数
        """
        self.listWidget.itemClicked.connect(self.listWidgetItemClicked)  # 连接列表项点击信号和槽函数
        self.okPb.clicked.connect(lambda: self.renderApplyPbClicked(needClose=True))  # 连接确定按钮点击信号和槽函数
        self.cancelPb.clicked.connect(self.close)  # 连接取消按钮点击信号和槽函数
        self.applyPb.clicked.connect(lambda: self.renderApplyPbClicked(needClose=False))  # 连接应用按钮点击信号和槽函数
        self.vecterRenderCB.currentIndexChanged.connect(self.vecterRenderCBChanged)  # 连接矢量渲染方式下拉框的索引改变信号和槽函数

    def vecterRenderCBChanged(self):
        """
        切换矢量图层渲染方式
        """
        self.comboTabWidget.setCurrentIndex(self.vecterRenderCB.currentIndex())  # 设置渲染选项卡栏的当前索引为矢量渲染下拉框的当前索引

    def initInfomationTab(self):
        """
        初始化信息选项卡
        """
        if type(self.layer) == QgsRasterLayer:  # 如果是栅格图层
            rasterLayerDict = getRasterLayerAttrs(self.layer)  # 获取栅格图层属性字典
            # 在界面上显示栅格图层属性信息
            self.rasterNameLabel.setText(rasterLayerDict['name'])
            self.rasterSourceLabel.setText(rasterLayerDict['source'])
            self.rasterMemoryLabel.setText(rasterLayerDict['memory'])
            self.rasterExtentLabel.setText(rasterLayerDict['extent'])
            self.rasterWidthLabel.setText(rasterLayerDict['width'])
            self.rasterHeightLabel.setText(rasterLayerDict['height'])
            self.rasterDataTypeLabel.setText(rasterLayerDict['dataType'])
            self.rasterBandNumLabel.setText(rasterLayerDict['bands'])
            self.rasterCrsLabel.setText(rasterLayerDict['crs'])
            # 添加栅格图层渲染控件
            self.rasterRenderWidget = QgsRendererRasterPropertiesWidget(self.layer, self.parentWindow.mapCanvas, parent=self)
            self.layerRenderLayout.addWidget(self.rasterRenderWidget)
        elif type(self.layer) == QgsVectorLayer:  # 如果是矢量图层
            vectorLayerDict = getVectorLayerAttrs(self.layer)  # 获取矢量图层属性字典
            # 在界面上显示矢量图层属性信息
            self.vectorNameLabel.setText(vectorLayerDict['name'])
            self.vectorSourceLabel.setText(vectorLayerDict['source'])
            self.vectorMemoryLabel.setText(vectorLayerDict['memory'])
            self.vectorExtentLabel.setText(vectorLayerDict['extent'])
            self.vectorGeoTypeLabel.setText(vectorLayerDict['geoType'])
            self.vectorFeatureNumLabel.setText(vectorLayerDict['featureNum'])
            self.vectorEncodingLabel.setText(vectorLayerDict['encoding'])
            self.vectorCrsLabel.setText(vectorLayerDict['crs'])
            self.vectorDpLabel.setText(vectorLayerDict['dpSource'])

            # 单一符号渲染
            self.vectorSingleRenderWidget = QgsSingleSymbolRendererWidget(self.layer, QgsStyle.defaultStyle(), self.layer.renderer())
            self.singleRenderLayout.addWidget(self.vectorSingleRenderWidget)

            # 分类符号渲染
            self.vectorCateGoryRenderWidget = QgsCategorizedSymbolRendererWidget(self.layer, QgsStyle.defaultStyle(), self.layer.renderer())
            self.cateRenderLayout.addWidget(self.vectorCateGoryRenderWidget)

    def decideRasterNVector(self, index):
        """
        决定是栅格还是矢量图层
        :param index: 当前索引
        """
        if index == 0:
            if type(self.layer) == QgsRasterLayer:  # 如果是栅格图层
                self.tabWidget.setCurrentIndex(0)  # 设置选项卡栏当前索引为 0
            elif type(self.layer) == QgsVectorLayer:  # 如果是矢量图层
                self.tabWidget.setCurrentIndex(1)  # 设置选项卡栏当前索引为 1
        elif index == 1:
            if type(self.layer) == QgsRasterLayer:  # 如果是栅格图层
                self.tabWidget.setCurrentIndex(2)  # 设置选项卡栏当前索引为 2
            elif type(self.layer) == QgsVectorLayer:  # 如果是矢量图层
                self.tabWidget.setCurrentIndex(3)  # 设置选项卡栏当前索引为 3

    def listWidgetItemClicked(self, item: QListWidgetItem):
        """
        列表项点击事件处理函数
        :param item: QListWidgetItem 对象
        """
        tempIndex = self.listWidget.indexFromItem(item).row()  # 获取点击的列表项的行索引
        self.decideRasterNVector(tempIndex)  # 根据索引决定是栅格还是矢量图层

    def renderApplyPbClicked(self, needClose=False):
        """
        渲染应用按钮点击事件处理函数
        :param needClose: 是否需要关闭窗口，默认为 False
        """
        if self.tabWidget.currentIndex() <= 1:  # 如果当前选项卡索引小于等于 1（即非渲染选项卡）
            print("没有在视图里，啥也不干")
        elif type(self.layer) == QgsRasterLayer:  # 如果是栅格图层
            self.rasterRenderWidget: QgsRendererRasterPropertiesWidget
            self.rasterRenderWidget.apply()  # 应用栅格图层渲染属性
        elif type(self.layer) == QgsVectorLayer:  # 如果是矢量图层
            print("矢量渲染")
            self.layer: QgsVectorLayer
            if self.comboTabWidget.currentIndex() == 0:  # 如果当前渲染选项卡索引为 0
                renderer = self.vectorSingleRenderWidget.renderer()  # 获取单一符号渲染器
            else:  # 否则
                renderer = self.vectorCateGoryRenderWidget.renderer()  # 获取分类符号渲染器
            self.layer.setRenderer(renderer)  # 设置图层渲染器
            self.layer.triggerRepaint()  # 触发重绘
        self.parentWindow.mapCanvas.refresh()  # 刷新地图画布
        if needClose:  # 如果需要关闭窗口
            self.close()  # 关闭窗口
