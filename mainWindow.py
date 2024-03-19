# 导入需要的qgis和PyQt5模块
from qgis.core import QgsProject, QgsLayerTreeModel
from qgis.gui import QgsLayerTreeView, QgsMapCanvas, QgsLayerTreeMapCanvasBridge
# noinspection PyUnresolvedReferences
from PyQt5.QtCore import QUrl, QSize, QMimeData, QUrl
from ui.myWindow import Ui_MainWindow
# noinspection PyUnresolvedReferences
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox

# 获取当前QGIS项目实例
PROJECT = QgsProject.instance()
# 导入自定义的函数
from qgisUtils import addMapLayer, readVectorFile, readRasterFile, menuProvider


# 一个基于QGIS和PyQt5的自定义主窗口类，用于展示和操作GIS数据
# 定义主窗口类，继承自QMainWindow和UI类
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()  # 调用父类构造器
        self.setupUi(self)  # 设置UI布局
        # 1 修改标题
        self.setWindowTitle("QGIS自定义界面")
        # 2 初始化图层树
        vl = QVBoxLayout(self.dockWidgetContents)
        self.layerTreeView = QgsLayerTreeView(self)
        vl.addWidget(self.layerTreeView)
        # 3 初始化地图画布
        self.mapCanvas = QgsMapCanvas(self)
        hl = QHBoxLayout(self.frame)
        hl.setContentsMargins(0, 0, 0, 0)  # 设置周围间距
        hl.addWidget(self.mapCanvas)
        # 4 设置图层树风格
        self.model = QgsLayerTreeModel(PROJECT.layerTreeRoot(), self)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)  # 允许图层节点重命名
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)  # 允许图层拖拽排序
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)  # 允许改变图层节点可视性
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)  # 展示图例
        self.model.setAutoCollapseLegendNodes(10)  # 当节点数大于等于10时自动折叠
        self.layerTreeView.setModel(self.model)
        # 4 建立图层树与地图画布的桥接，使图层的变化反映在地图上
        self.layerTreeBridge = QgsLayerTreeMapCanvasBridge(PROJECT.layerTreeRoot(), self.mapCanvas, self)
        # 5 初始加载影像
        self.firstAdd = True
        # 6 允许拖拽文件
        self.setAcceptDrops(True)
        # 7 图层树右键菜单创建
        self.rightMenuProv = menuProvider(self)
        self.layerTreeView.setMenuProvider(self.rightMenuProv)
        # A 连接按钮和菜单栏的点击事件到相应的槽函数
        self.connectFunc()

    # 连接动作的触发信号到对应的处理函数
    def connectFunc(self):
        self.actionOpenRaster.triggered.connect(self.actionOpenRasterTriggered)
        self.actionOpenShp.triggered.connect(self.actionOpenShpTriggered)

    # 拖拽文件进入事件
    def dragEnterEvent(self, fileData):
        if fileData.mimeData().hasUrls():  # 检查拖拽数据是否包含URL
            fileData.accept()  # 接受拖拽
        else:
            fileData.ignore()  # 忽略非URL拖拽

    # 拖拽文件事件
    def dropEvent(self, fileData):
        mimeData: QMimeData = fileData.mimeData()
        # 获取拖拽放下的文件路径列表
        filePathList = [u.path()[1:] for u in mimeData.urls()]
        for filePath in filePathList:
            # 替换路径分隔符以适应Windows环境
            filePath: str = filePath.replace("/", "//")
            # 根据文件类型调用相应的添加图层函数
            if filePath.split(".")[-1] in ["tif", "TIF", "tiff", "TIFF", "GTIFF", "png", "jpg", "pdf"]:
                self.addRasterLayer(filePath)
            elif filePath.split(".")[-1] in ["shp", "SHP", "gpkg", "geojson", "kml"]:
                self.addVectorLayer(filePath)
            elif filePath == "":
                pass
            else:
                # 如果文件格式不支持，弹窗警告
                QMessageBox.about(self, '警告', f'{filePath}为不支持的文件类型，目前支持栅格影像和shp矢量')

    # "打开栅格文件"动作的触发函数
    def actionOpenRasterTriggered(self):
        # 打开文件对话框，并设置支持的文件筛选器
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '',
                                                     'GeoTiff(*.tif;*tiff;*TIF;*TIFF);;All Files(*);;JPEG(*.jpg;*.jpeg;*.JPG;*.JPEG);;*.png;;*.pdf')
        if data_file:
            # 如果成功选择文件，添加栅格图层
            self.addRasterLayer(data_file)

    # "打开矢量文件"动作的触发函数
    def actionOpenShpTriggered(self):
        # 打开文件对话框，并设置支持的文件筛选器
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '',
                                                     "ShapeFile(*.shp);;All Files(*);;Other(*.gpkg;*.geojson;*.kml)")
        if data_file:
            # 如果成功选择文件，添加矢量图层
            self.addVectorLayer(data_file)

    # 添加栅格图层的函数
    def addRasterLayer(self, rasterFilePath):
        # 使用工具函数读取栅格文件并创建图层
        rasterLayer = readRasterFile(rasterFilePath)
        # 判断是否是第一次添加图层，如果是，将图层添加到地图和设置地图的属性
        if self.firstAdd:
            addMapLayer(rasterLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(rasterLayer, self.mapCanvas)

    # 添加矢量图层的函数
    def addVectorLayer(self, vectorFilePath):
        # 使用工具函数读取矢量文件并创建图层
        vectorLayer = readVectorFile(vectorFilePath)
        # 判断是否是第一次添加图层，如果是，将图层添加到地图和设置地图的属性
        if self.firstAdd:
            addMapLayer(vectorLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(vectorLayer, self.mapCanvas)
