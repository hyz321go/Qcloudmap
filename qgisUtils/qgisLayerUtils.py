from qgis.core import QgsMapLayer,QgsRasterLayer,QgsVectorLayer
import os
import os.path as osp

def readRasterFile(rasterFilePath):
    rasterLayer = QgsRasterLayer(rasterFilePath,osp.basename(rasterFilePath))
    return rasterLayer

def getRasterLayerAttrs(rasterLayer:QgsRasterLayer):
    print("name: ", rasterLayer.name()) # 图层名
    print("type: ", rasterLayer.type()) # 栅格还是矢量图层
    print("height - width: ", rasterLayer.height(),rasterLayer.width()) #尺寸
    print("bands: ", rasterLayer.bandCount()) #波段数
    print("extent", rasterLayer.extent()) #外接矩形范围
    print("source", rasterLayer.source()) #图层的源文件地址
    print("crs", rasterLayer.crs())  # 图层的坐标系统

if __name__ == '__main__':
    tifPath = r"G:\QGIS\myData\ca_nrc_CGG2013an83.tif"
    tifLayer = readRasterFile(tifPath)
    getRasterLayerAttrs(tifLayer)
