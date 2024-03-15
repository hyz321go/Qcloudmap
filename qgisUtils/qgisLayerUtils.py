from qgis.core import QgsMapLayer,QgsRasterLayer,QgsVectorLayer,QgsProject
from qgis.gui import QgsMapCanvas
import os
import os.path as osp

PROJECT = QgsProject.instance()

# 加载图层的函数
def addMapLayer(layer:QgsMapLayer,mapCanvas:QgsMapCanvas,firstAddLayer=False):
    if layer.isValid():
        if firstAddLayer:
            mapCanvas.setDestinationCrs(layer.crs())
            mapCanvas.setExtent(layer.extent())

        while(PROJECT.mapLayersByName(layer.name())):
            layer.setName(layer.name()+"_1")

        PROJECT.addMapLayer(layer)
        layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]
        mapCanvas.setLayers(layers)
        mapCanvas.refresh()

def readRasterFile(rasterFilePath):
    rasterLayer = QgsRasterLayer(rasterFilePath,osp.basename(rasterFilePath))
    return rasterLayer

def readVectorFile(vectorFilePath):
    vectorLayer = QgsVectorLayer(vectorFilePath,osp.basename(vectorFilePath),"ogr")
    return vectorLayer

def getRasterLayerAttrs(rasterLayer:QgsRasterLayer):
    print("name: ", rasterLayer.name()) # 图层名
    print("type: ", rasterLayer.type()) # 栅格还是矢量图层
    print("height - width: ", rasterLayer.height(),rasterLayer.width()) #尺寸
    print("bands: ", rasterLayer.bandCount()) #波段数
    print("extent", rasterLayer.extent()) #外接矩形范围
    print("source", rasterLayer.source()) #图层的源文件地址
    print("crs", rasterLayer.crs())  # 图层的坐标系统

def getVectorLayerAttrs(vectorLayer:QgsVectorLayer):
    print("name: ", vectorLayer.name())  # 图层名
    print("type: ", vectorLayer.type())  # 栅格还是矢量图层
    print("extent", vectorLayer.extent())  # 外接矩形范围
    print("source", vectorLayer.source())  # 图层的源文件地址
    print("crs", vectorLayer.crs())  # 图层的坐标系统