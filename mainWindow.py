import sys
import traceback
# 导入系统模块和错误回溯模块，用于执行系统相关的操作和捕获异常错误。

from qgis.core import QgsProject,QgsLayerTreeModel,QgsCoordinateReferenceSystem,QgsMapSettings,QgsMapLayer,QgsVectorLayer,QgsMapLayerType
# 导入QGIS核心库，包括项目管理、图层树模型、坐标参考系统和地图设置。

from qgis.gui import QgsLayerTreeView,QgsMapCanvas,QgsLayerTreeMapCanvasBridge,QgsMapToolIdentifyFeature
# 导入QGIS图形用户界面库，包括图层树视图、地图画布和图层树与地图画布桥接工具。

from PyQt5.QtCore import QUrl,QSize,QMimeData,QUrl,Qt
# 导入PyQt5核心模块，用于处理URL、尺寸、MIME数据等。

from ui.myWindow import Ui_MainWindow
# 从ui模块导入用户主窗口界面。

from PyQt5.QtWidgets import QMainWindow,QVBoxLayout,QHBoxLayout,QFileDialog,QMessageBox,QStatusBar,QLabel,QComboBox
# 导入PyQt5控件模块，包括主窗口、垂直和水平布局、文件对话框、消息盒子、状态栏、标签、组合框等控件。

from qgisUtils import addMapLayer,readVectorFile,readRasterFile,menuProvider,PolygonMapTool
# 导入自定义的QGIS工具模块，用于添加地图图层、读取矢量和栅格文件、创建右键菜单提供者。

PROJECT = QgsProject.instance()
# 获取当前QGIS项目的实例。

class MainWindow(QMainWindow, Ui_MainWindow):
    # 定义主窗口类，继承自QMainWindow和Ui_MainWindow。

    def __init__(self):
        # 初始化构造函数。
        super(MainWindow, self).__init__()
        # 调用父类的构造函数。
        self.setupUi(self)
        # 初始化用户界面。

        # 1 修改标题
        self.setWindowTitle("QGIS自定义界面")
        # 设置主窗口的标题为"QGIS自定义界面"。

        # 2 初始化图层树
        vl = QVBoxLayout(self.dockWidgetContents)
        # 在dockWidgetContents上创建一个新的垂直布局。
        self.layerTreeView = QgsLayerTreeView(self)
        # 创建一个图层树视图对象。
        vl.addWidget(self.layerTreeView)
        # 在垂直布局中添加图层树视图。

        # 3 初始化地图画布
        self.mapCanvas : QgsMapCanvas = QgsMapCanvas(self)
        # 创建一个新的地图画布对象。
        self.hl = QHBoxLayout(self.frame)
        # 在frame上创建一个新的水平布局。
        self.hl.setContentsMargins(0,0,0,0) #设置周围间距
        # 设置水平布局的内容边距为0。
        self.hl.addWidget(self.mapCanvas)
        # 在水平布局中添加地图画布。

        # 4 设置图层树风格
        self.model = QgsLayerTreeModel(PROJECT.layerTreeRoot(),self)
        # 创建一个图层树模型对象，基于当前项目的图层树根。

        # 允许图层节点重命名、拖拽排序、改变节点可视性、展示图例，并且当节点数大于等于10时自动折叠
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)
        self.model.setAutoCollapseLegendNodes(10)
        self.layerTreeView.setModel(self.model)
        # 设置图层树视图使用前面创建的图层树模型。

        # 4 建立图层树与地图画布的桥接
        self.layerTreeBridge = QgsLayerTreeMapCanvasBridge(PROJECT.layerTreeRoot(),self.mapCanvas,self)
        # 创建一个图层树到地图画布的桥接对象。

        # 5 初始加载影像标志，用以判断是否是第一次添加图层，以决定是否将它设定为焦点图层
        self.firstAdd = True

        # 6 允许拖拽文件到主窗口中
        self.setAcceptDrops(True)

        # 7 图层树右键菜单创建
        self.rightMenuProv = menuProvider(self)
        # 创建一个自定义的右键菜单提供者。
        self.layerTreeView.setMenuProvider(self.rightMenuProv)
        # 为图层树视图设置右键菜单提供者。

        # 8.0 提前给予基本CRS
        self.mapCanvas.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        # 设置画布的目标坐标参考系统为WGS 84。

        # 8 状态栏控件
        # 创建状态栏，并进行配置，用于显示坐标、比例尺和坐标系信息。
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet('color: black; border: none')
        self.statusXY = QLabel('{:<40}'.format('')) # x y 坐标状态
        self.statusBar.addWidget(self.statusXY,1)

        self.statusScaleLabel = QLabel('比例尺')
        self.statusScaleComboBox = QComboBox(self)
        self.statusScaleComboBox.setFixedWidth(120)
        self.statusScaleComboBox.addItems(["1:500","1:1000","1:2500","1:5000","1:10000","1:25000","1:100000","1:500000","1:1000000"])
        self.statusScaleComboBox.setEditable(True)
        self.statusBar.addWidget(self.statusScaleLabel)
        self.statusBar.addWidget(self.statusScaleComboBox)

        self.statusCrsLabel = QLabel(f"坐标系: {self.mapCanvas.mapSettings().destinationCrs().description()}-{self.mapCanvas.mapSettings().destinationCrs().authid()}")
        self.statusBar.addWidget(self.statusCrsLabel)

        self.setStatusBar(self.statusBar)
        # 将上述创建的状态栏设置为窗口的状态栏。

        # 9 error catch
        # 配置全局异常捕获，以便在错误发生时显示弹窗。
        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_exceptions

        # A 按钮、菜单栏功能
        # 连接操作和信号
        self.connectFunc()
        # B 初始设置控件
        self.actionEditShp.setEnabled(False)
        self.editTempLayer: QgsVectorLayer = None  # 初始编辑图层为None

    def connectFunc(self):
        # 定义连接函数，用于连接GUI组件和方法。

        # 每次移动鼠标，坐标和比例尺变化
        # 连接地图画布的信号到方法以显示当前的坐标和比例尺。
        self.mapCanvas.xyCoordinates.connect(self.showXY)
        self.mapCanvas.scaleChanged.connect(self.showScale)
        self.mapCanvas.destinationCrsChanged.connect(self.showCrs)
        self.statusScaleComboBox.editTextChanged.connect(self.changeScaleForString)

        # action连线到相应的槽函数，以触发对应的功能，如打开栅格数据或矢量数据。
        self.actionOpenRaster.triggered.connect(self.actionOpenRasterTriggered)
        self.actionOpenShp.triggered.connect(self.actionOpenShpTriggered)

        # action edit
        self.actionSelectFeature.triggered.connect(self.actionSelectFeatureTriggered)
        self.actionEditShp.triggered.connect(self.actionEditShpTriggered)
        self.actionDeleteFeature.triggered.connect(self.actionDeleteFeatureTriggered)
        self.actionPolygon.triggered.connect(self.actionPolygonTriggered)
        # 单击、双击图层 触发事件
        self.layerTreeView.clicked.connect(self.layerClicked)

    # 定义actionDeleteFeatureTriggered函数，当删除要素动作被触发时调用
    def actionDeleteFeatureTriggered(self):
        # 如果当前没有处于编辑状态的图层，则弹出信息框提示用户
        if self.editTempLayer == None:
            QMessageBox.information(self, '警告', '您没有编辑中的矢量')
            return  # 提前返回，不执行后续代码
        # 如果当前编辑图层中没有选中的要素，则弹出信息框提示用户
        if len(self.editTempLayer.selectedFeatureIds()) == 0:
            QMessageBox.information(self, '删除选中矢量', '您没有选择任何矢量')
        else:
            # 如果有选中的要素，则调用图层的deleteSelectedFeatures方法删除这些要素
            self.editTempLayer.deleteSelectedFeatures()

    # 当图层被点击时调用的函数
    def layerClicked(self):
        # 获取当前选中的图层
        curLayer: QgsMapLayer = self.layerTreeView.currentLayer()
        # 如果当前图层存在，且为QgsVectorLayer类型，且不是只读的，则启用编辑动作
        if curLayer and type(curLayer) == QgsVectorLayer and not curLayer.readOnly():
            self.actionEditShp.setEnabled(True)
        else:
            # 否则，禁用编辑动作
            self.actionEditShp.setEnabled(False)

    # 当编辑Shapefile动作被触发时调用的函数
    def actionEditShpTriggered(self):
        # 如果编辑动作被选中
        if self.actionEditShp.isChecked():
            # 获取当前选中的图层，并赋值给临时编辑图层变量
            self.editTempLayer: QgsVectorLayer = self.layerTreeView.currentLayer()
            # 开始编辑当前图层
            self.editTempLayer.startEditing()
        else:
            # 如果编辑动作没有被选中，弹出消息框询问用户是否保存编辑
            saveShpEdit = QMessageBox.question(self, '保存编辑', "确定要将编辑内容保存到内存吗？",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            # 如果用户选择是，则提交编辑内容
            if saveShpEdit == QMessageBox.Yes:
                self.editTempLayer.commitChanges()
            else:
                # 如果用户选择否，则回滚编辑内容
                self.editTempLayer.rollBack()

            # 刷新地图画布显示最新的图层状态
            self.mapCanvas.refresh()
            # 清空临时编辑图层变量
            self.editTempLayer = None

    # 定义selectToolIdentified函数，当特定要素被识别时调用
    def selectToolIdentified(self, feature):
        # 打印被识别要素的ID
        print(feature.id())
        # 获取当前图层
        layerTemp: QgsVectorLayer = self.layerTreeView.currentLayer()
        # 检查当前图层是否为矢量图层
        if layerTemp.type() == QgsMapLayerType.VectorLayer:
            # 如果要素已经被选中，则取消选中
            if feature.id() in layerTemp.selectedFeatureIds():
                layerTemp.deselect(feature.id())
            # 否则，移除所有选中的要素并选中当前要素
            else:
                layerTemp.removeSelection()
                layerTemp.select(feature.id())

    # 定义actionSelectFeatureTriggered函数，当选择要素动作被触发时调用
    def actionSelectFeatureTriggered(self):
        # 检查选择要素动作是否被激活
        if self.actionSelectFeature.isChecked():
            # 如果当前有激活的地图工具，则取消激活
            if self.mapCanvas.mapTool():
                self.mapCanvas.unsetMapTool(self.mapCanvas.mapTool())
            # 创建一个QgsMapToolIdentifyFeature对象
            self.selectTool = QgsMapToolIdentifyFeature(self.mapCanvas)
            # 设置鼠标光标为箭头
            self.selectTool.setCursor(Qt.ArrowCursor)
            # 连接featureIdentified信号到selectToolIdentified函数
            self.selectTool.featureIdentified.connect(self.selectToolIdentified)
            # 获取地图画布上的图层列表
            layers = self.mapCanvas.layers()
            # 如果图层列表不为空，则设置选择工具的当前图层为图层树视图中的当前图层
            if layers:
                self.selectTool.setLayer(self.layerTreeView.currentLayer())
            # 设置地图画布的当前地图工具为selectTool
            self.mapCanvas.setMapTool(self.selectTool)
        # 如果选择要素动作没有被激活
        else:
            # 如果当前有激活的地图工具，则取消激活
            if self.mapCanvas.mapTool():
                self.mapCanvas.unsetMapTool(self.mapCanvas.mapTool())

    def showXY(self, point):
        # 定义显示坐标的方法。
        x = point.x()
        y = point.y()
        self.statusXY.setText(f'{x:.6f}, {y:.6f}')
        # 在状态栏中显示当前鼠标所在位置的X和Y坐标。

    def showScale(self, scale):
        # 定义显示比例尺的方法。
        self.statusScaleComboBox.setEditText(f"1:{int(scale)}")
        # 在状态栏中更新当前的比例尺。

    def showCrs(self):
        # 定义显示坐标系的方法。
        mapSetting : QgsMapSettings = self.mapCanvas.mapSettings()
        self.statusCrsLabel.setText(f"坐标系: {mapSetting.destinationCrs().description()}-{mapSetting.destinationCrs().authid()}")
        # 在状态栏中显示当前地图的坐标参照系统及其授权标识。

    def changeScaleForString(self, str):
        # 定义根据输入的字符串改变比例尺的方法。
        try:
            left, right = str.split(":")[0], str.split(":")[-1]
            if int(left) == 1 and int(right) > 0 and int(right) != int(self.mapCanvas.scale()):
                self.mapCanvas.zoomScale(int(right))
                self.mapCanvas.zoomWithCenter()
        except:
            print(traceback.format_stack())
            # 如果比例尺更改出错，则打印错误堆栈信息。

    def dragEnterEvent(self, fileData):
        # 定义拖拽文件进入窗口事件的处理方法。
        if fileData.mimeData().hasUrls():
            fileData.accept()
        else:
            fileData.ignore()
            # 如果拖拽文件包含URL则接受，否则忽略。

    # 拖拽文件事件
    # 定义文件被拖拽放下时的处理方法。
    def dropEvent(self, fileData):
        mimeData: QMimeData = fileData.mimeData()
        filePathList = [u.path()[1:] for u in mimeData.urls()]
        for filePath in filePathList:
            filePath:str = filePath.replace("/","//")
            if filePath.split(".")[-1] in ["tif", "TIF", "tiff", "TIFF", "GTIFF", "png", "jpg", "pdf"]:
                # 如果文件是栅格影像类型，则添加为栅格图层。
                self.addRasterLayer(filePath)
            elif filePath.split(".")[-1] in ["shp", "SHP", "gpkg", "geojson", "kml"]:
                # 如果文件是矢量数据类型，则添加为矢量图层。
                self.addVectorLayer(filePath)
            elif filePath == "":
                pass
            else:
                QMessageBox.about(self, '警告', f'{filePath}为不支持的文件类型，目前支持栅格影像和shp矢量')
                # 如果文件类型不支持，则弹出警告框。

    def catch_exceptions(self, ty, value, trace):
        """
        捕获异常，并弹窗显示
        :param ty: 异常的类型
        :param value: 异常的对象
        :param trace: 异常的traceback
        """
        traceback_format = traceback.format_exception(ty, value, trace)
        traceback_string = "".join(traceback_format)
        QMessageBox.about(self, 'error', traceback_string)
        # 弹出窗口显示异常信息。
        self.old_hook(ty, value, trace)
        # 调用之前保存的原始异常处理方法。

    def actionOpenRasterTriggered(self):
        # 定义打开栅格数据功能。
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '','GeoTiff(*.tif;*tiff;*TIF;*TIFF);;All Files(*);;JPEG(*.jpg;*.jpeg;*.JPG;*.JPEG);;*.png;;*.pdf')
        if data_file:
            self.addRasterLayer(data_file)
            # 如果选中了数据文件，则添加栅格图层。

    def actionOpenShpTriggered(self):
        # 定义打开矢量数据功能。
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '',"ShapeFile(*.shp);;All Files(*);;Other(*.gpkg;*.geojson;*.kml)")
        if data_file:
            self.addVectorLayer(data_file)
            # 如果选中了数据文件，则添加矢量图层。

    # 添加栅格图层
    # 定义添加栅格图层的方法。
    def addRasterLayer(self, rasterFilePath):
        rasterLayer = readRasterFile(rasterFilePath)
        if self.firstAdd:
            addMapLayer(rasterLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(rasterLayer, self.mapCanvas)
            # 根据是否是第一次添加图层来执行不同的操作。

    # 添加矢量图层
    # 定义添加矢量图层的方法。
    def addVectorLayer(self, vectorFilePath):
        vectorLayer = readVectorFile(vectorFilePath)
        if self.firstAdd:
            addMapLayer(vectorLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(vectorLayer, self.mapCanvas)
            # 根据是否是第一次添加图层来执行不同的操作。

    # 定义当触发多边形动作时执行的函数。
    def actionPolygonTriggered(self):
        # 如果当前编辑层为None，说明没有被选中的矢量层进行编辑。
        if self.editTempLayer == None:
            # 使用QMessageBox弹出信息框提示用户，需要有一个正在编辑的矢量层。
            QMessageBox.information(self, '警告', '您没有编辑中的矢量')
            return  # 返回，不继续执行后续代码。
        # 检查当前地图画布（mapCanvas）上是否有激活的地图工具。
        if self.mapCanvas.mapTool():
            # 如果有，则调用该工具的deactivate方法来停用它。
            self.mapCanvas.mapTool().deactivate()
        # 创建一个多边形工具实例（PolygonMapTool），用于在地图上绘制多边形。
        # 它需要地图画布对象、正在编辑的临时图层对象和主窗口对象作为参数。
        self.polygonTool = PolygonMapTool(self.mapCanvas, self.editTempLayer, self)
        # 将当前的地图工具设置为这个新创建的多边形工具。
        self.mapCanvas.setMapTool(self.polygonTool)