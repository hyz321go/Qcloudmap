from qgis.core import QgsMapLayer,QgsRasterLayer,QgsVectorLayer
import os
import os.path as osp

def readVectorFile(vectorFilePath):
    vectorLayer = QgsVectorLayer(vectorFilePath,osp.basename(vectorFilePath),"ogr")
    return vectorLayer

def getVectorLayerAttrs(vectorLayer:QgsVectorLayer):
    print("name: ", vectorLayer.name())  # 图层名
    print("type: ", vectorLayer.type())  # 栅格还是矢量图层
    print("extent", vectorLayer.extent())  # 外接矩形范围
    print("source", vectorLayer.source())  # 图层的源文件地址
    print("crs", vectorLayer.crs())  # 图层的坐标系统

if __name__ == '__main__':
    shpPath = r"G:\QGIS\myData\naturalearth_lowres.shp"
    shpLayer = readVectorFile(shpPath)
    getVectorLayerAttrs(shpLayer)
