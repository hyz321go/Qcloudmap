from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsProject, QgsRasterDataProvider, QgsVectorDataProvider, QgsRectangle, QgsCoordinateReferenceSystem, QgsWkbTypes
from qgis.gui import QgsMapCanvas
import os
import os.path as osp
from qgisUtils.yoyiFile import getFileSize  # 导入自定义模块中的函数
PROJECT = QgsProject.instance()  # 获取QGIS项目实例

def addMapLayer(layer: QgsMapLayer, mapCanvas: QgsMapCanvas, firstAddLayer=False):
    """
    将图层添加到地图中，并更新地图画布

    Args:
    layer (QgsMapLayer): 要添加的图层对象
    mapCanvas (QgsMapCanvas): 地图画布对象
    firstAddLayer (bool, optional): 是否是第一次添加图层，默认为False

    Returns:
    None
    """
    if layer.isValid():  # 检查图层是否有效
        if firstAddLayer:  # 如果是第一次添加图层
            mapCanvas.setDestinationCrs(layer.crs())  # 设置地图画布的目标坐标参考系统为图层的坐标参考系统
            mapCanvas.setExtent(layer.extent())  # 设置地图画布的范围为图层的范围

        while(PROJECT.mapLayersByName(layer.name())):  # 如果存在同名图层
            layer.setName(layer.name()+"_1")  # 给图层重命名，加上后缀"_1"

        PROJECT.addMapLayer(layer)  # 将图层添加到QGIS项目中
        layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]  # 获取所有图层对象，并将当前图层添加到列表中
        mapCanvas.setLayers(layers)  # 设置地图画布的图层列表
        mapCanvas.refresh()  # 刷新地图画布

def readRasterFile(rasterFilePath):
    """
    读取栅格文件并创建栅格图层对象

    Args:
    rasterFilePath (str): 栅格文件路径

    Returns:
    QgsRasterLayer: 创建的栅格图层对象
    """
    rasterLayer = QgsRasterLayer(rasterFilePath, osp.basename(rasterFilePath))  # 使用栅格文件路径创建栅格图层对象
    return rasterLayer  # 返回栅格图层对象

def readVectorFile(vectorFilePath):
    """
    读取矢量文件并创建矢量图层对象

    Args:
    vectorFilePath (str): 矢量文件路径

    Returns:
    QgsVectorLayer: 创建的矢量图层对象
    """
    vectorLayer = QgsVectorLayer(vectorFilePath, osp.basename(vectorFilePath), "ogr")  # 使用矢量文件路径创建矢量图层对象
    return vectorLayer  # 返回矢量图层对象

qgisDataTypeDict = {
    0: "UnknownDataType",
    1: "Uint8",
    2: "UInt16",
    3: "Int16",
    4: "UInt32",
    5: "Int32",
    6: "Float32",
    7: "Float64",
    8: "CInt16",
    9: "CInt32",
    10: "CFloat32",
    11: "CFloat64",
    12: "ARGB32",
    13: "ARGB32_Premultiplied"
}

def getRasterLayerAttrs(rasterLayer: QgsRasterLayer):
    """
    获取栅格图层的属性并以字典形式返回

    Args:
    rasterLayer (QgsRasterLayer): 要获取属性的栅格图层对象

    Returns:
    dict: 包含栅格图层属性的字典
    """
    rdp: QgsRasterDataProvider = rasterLayer.dataProvider()  # 获取栅格数据提供者
    crs: QgsCoordinateReferenceSystem = rasterLayer.crs()  # 获取坐标参考系统
    extent: QgsRectangle = rasterLayer.extent()  # 获取图层范围

    # 构建属性字典
    resDict = {
        "name": rasterLayer.name(),  # 图层名称
        "source": rasterLayer.source(),  # 图层源文件路径
        "memory": getFileSize(rasterLayer.source()),  # 图层所占内存大小
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",  # 图层范围
        "width": f"{rasterLayer.width()}",  # 图层宽度（像素）
        "height": f"{rasterLayer.height()}",  # 图层高度（像素）
        "dataType": qgisDataTypeDict[rdp.dataType(1)],  # 图层数据类型
        "bands": f"{rasterLayer.bandCount()}",  # 图层波段数
        "crs": crs.description()  # 图层坐标参考系统描述
    }
    return resDict  # 返回包含栅格图层属性的字典

def getVectorLayerAttrs(vectorLayer: QgsVectorLayer):
    """
    获取矢量图层的属性并以字典形式返回

    Args:
    vectorLayer (QgsVectorLayer): 要获取属性的矢量图层对象

    Returns:
    dict: 包含矢量图层属性的字典
    """
    vdp: QgsVectorDataProvider = vectorLayer.dataProvider()  # 获取矢量数据提供者
    crs: QgsCoordinateReferenceSystem = vectorLayer.crs()  # 获取坐标参考系统
    extent: QgsRectangle = vectorLayer.extent()  # 获取图层范围

    # 构建属性字典
    resDict = {
        "name": vectorLayer.name(),  # 图层名称
        "source": vectorLayer.source(),  # 图层源文件路径
        "memory": getFileSize(vectorLayer.source()),  # 图层所占内存大小
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",  # 图层范围
        "geoType": QgsWkbTypes.geometryDisplayString(vectorLayer.geometryType()),  # 几何类型
        "featureNum": f"{vectorLayer.featureCount()}",  # 要素数量
        "encoding": vdp.encoding(),  # 编码方式
        "crs": crs.description(),  # 坐标参考系统描述
        "dpSource": vdp.description()  # 数据提供者描述
    }
    return resDict  # 返回包含矢量图层属性的字典

if __name__ == '__main__':
    layer = QgsVectorLayer(r"G:\QGIS\myData\naturalearth_lowres.shp")
    print(getVectorLayerAttrs(layer))
