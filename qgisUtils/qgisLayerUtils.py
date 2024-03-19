from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.gui import QgsMapCanvas
import os
import os.path as osp
# 提供一系列操作和查询地图图层的接口

# 获取当前QGIS项目实例
PROJECT = QgsProject.instance()

# 定义函数addMapLayer，用于将图层添加到地图和项目中
def addMapLayer(layer: QgsMapLayer, mapCanvas: QgsMapCanvas, firstAddLayer=False):
    if layer.isValid():  # 检查图层是否有效
        if firstAddLayer:  # 如果是第一次添加图层，设置地图的坐标参考系统和范围
            mapCanvas.setDestinationCrs(layer.crs())
            mapCanvas.setExtent(layer.extent())

        # 确保没有同名图层，如果有，修改名称
        while(PROJECT.mapLayersByName(layer.name())):
            layer.setName(layer.name() + "_1")

        PROJECT.addMapLayer(layer)  # 添加图层到当前项目
        # 将新添加的图层放置在已有图层的上方
        layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]
        mapCanvas.setLayers(layers)  # 设置地图画布的图层
        mapCanvas.refresh()  # 刷新地图画布显示图层变更

# 定义函数readRasterFile，用于读取栅格文件并创建栅格图层
def readRasterFile(rasterFilePath):
    rasterLayer = QgsRasterLayer(rasterFilePath, osp.basename(rasterFilePath))  # 创建栅格图层
    return rasterLayer  # 返回创建的栅格图层

# 定义函数readVectorFile，用于读取矢量文件并创建矢量图层
def readVectorFile(vectorFilePath):
    vectorLayer = QgsVectorLayer(vectorFilePath, osp.basename(vectorFilePath), "ogr")  # 创建矢量图层
    return vectorLayer  # 返回创建的矢量图层

# 定义函数getRasterLayerAttrs，用于打印栅格图层的属性
def getRasterLayerAttrs(rasterLayer: QgsRasterLayer):
    # 打印各种栅格图层属性
    print("name: ", rasterLayer.name())  # 图层名
    print("type: ", rasterLayer.type())  # 栅格还是矢量图层
    print("height - width: ", rasterLayer.height(), rasterLayer.width())  # 尺寸
    print("bands: ", rasterLayer.bandCount())  # 波段数
    print("extent", rasterLayer.extent())  # 外接矩形范围
    print("source", rasterLayer.source())  # 图层的源文件地址
    print("crs", rasterLayer.crs())  # 图层的坐标系统

# 定义函数getVectorLayerAttrs，用于打印矢量图层的属性
def getVectorLayerAttrs(vectorLayer: QgsVectorLayer):
    # 打印各种矢量图层属性
    print("name: ", vectorLayer.name())  # 图层名
    print("type: ", vectorLayer.type())  # 栅格还是矢量图层
    print("extent", vectorLayer.extent())  # 外接矩形范围
    print("source", vectorLayer.source())  # 图层的源文件地址
    print("crs", vectorLayer.crs())  # 图层的坐标系统