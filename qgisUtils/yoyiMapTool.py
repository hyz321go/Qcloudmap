from osgeo import gdal
# import affine
import numpy as np
from qgis.PyQt.QtCore import Qt,QRectF, QPointF,QPoint
from qgis.PyQt.QtGui import QCursor,QPixmap,QPen, QColor
from qgis.PyQt.QtWidgets import QMessageBox,QUndoStack,QComboBox,QMenu,QAction
from qgis.core import QgsMapLayer,QgsRectangle,QgsPoint,QgsDistanceArea,QgsCircle,QgsPointXY, QgsWkbTypes,QgsVectorLayer,\
    QgsVectorDataProvider,QgsFeature,QgsGeometry,QgsPolygon,QgsLineString,QgsRasterLayer,QgsProject,QgsMapSettings, \
    QgsMapRendererParallelJob,QgsWkbTypes,QgsFeatureRequest,QgsMultiPolygon,QgsMapToPixel,QgsMultiLineString
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsVertexMarker,QgsMapToolIdentify,QgsMapTool,QgsMapToolIdentifyFeature,QgsMapCanvas,QgsMapCanvasItem,QgsMapToolPan

from widgetAndDialog.mapTool_InputAttrWindow import inputAttrWindowClass

# 实现了一个多边形绘制工具类 PolygonMapTool，继承自 QgsMapToolEmitPoint。它用于在地图上绘制多边形，并支持添加到指定图层中
class PolygonMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, layer, mainWindow, preField=None, preFieldValue=None, recExtent=None, otherCanvas=None, fieldValueDict=None, dialogMianFieldName=None):
        # 调用父类的初始化方法
        super(PolygonMapTool, self).__init__(canvas)
        # 设置类属性
        self.canvas = canvas
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)  # 创建一个橡皮筋对象，用于绘制多边形
        self.rubberBand.setColor(QColor(255, 0, 0, 50))  # 设置橡皮筋颜色为红色
        self.rubberBand.setWidth(1)  # 设置橡皮筋宽度为1个像素
        self.wkbType = "polygon"  # 几何类型为多边形
        self.editLayer: QgsVectorLayer = layer  # 要编辑的图层
        self.caps = self.editLayer.dataProvider().capabilities()  # 获取图层数据提供者的能力
        self.mainWindow = mainWindow  # 主窗口
        self.preField = preField  # 预设字段
        self.preFieldValue = preFieldValue  # 预设字段值
        self.fieldValueDict = fieldValueDict  # 字段值字典
        self.dialogMianFieldName = dialogMianFieldName  # 对话框主字段名
        self.recExtent: QgsRectangle = recExtent  # 记录范围
        self.otherCanvas = otherCanvas  # 其他画布
        self.reset()  # 重置方法

    def reset(self):
        # 重置方法，清空绘制状态和点集合
        self.is_start = False  # 开始绘图标志位
        self.is_vertical = False  # 垂直画线标志位
        self.cursor_point = None  # 当前光标点
        self.points = []  # 点集合
        self.rubberBand.reset()  # 重置橡皮筋

    def changeRubberBandColor(self, r, g, b):
        # 更改橡皮筋颜色
        self.rubberBand.setColor(QColor(r, g, b, 50))

    def changeFieldValue(self, fieldValue):
        # 更改字段值
        self.preFieldValue = fieldValue

    def canvasPressEvent(self, event):
        # 处理画布按下事件
        if event.button() == Qt.LeftButton:  # 左键按下
            self.points.append(self.cursor_point)  # 将当前光标点添加到点集合中
            self.is_start = True  # 设置开始绘图标志位为True
        elif event.button() == Qt.RightButton:  # 右键按下
            # 右键结束绘制
            if self.is_start:  # 如果已经开始绘图
                self.is_start = False  # 结束绘图
                self.cursor_point = None  # 清空当前光标点
                self.p = self.polygon()  # 获取绘制的多边形

                if self.recExtent and not QgsGeometry.fromRect(self.recExtent).contains(self.p):
                    # 如果绘制的多边形不在图层范围内
                    QMessageBox.about(self.mainWindow, '错误', "面矢量与图层范围不相交")  # 显示错误消息
                    self.reset()  # 重置绘图状态
                else:
                    if self.p is not None:  # 如果多边形存在
                        if self.p.isGeosValid():  # 如果多边形几何有效
                            self.addFeature()  # 添加要素
                        else:
                            QMessageBox.about(self.mainWindow, '错误', "面矢量拓扑逻辑错误")  # 显示错误消息
                            self.reset()  # 重置绘图状态
                    else:
                        self.reset()  # 重置绘图状态
            else:
                pass

    def addFeature(self):
        # 添加要素方法
        if self.caps & QgsVectorDataProvider.AddFeatures:  # 如果图层支持添加要素
            feat = QgsFeature(self.editLayer.fields())  # 创建要素对象
            inputAttrWindows = inputAttrWindowClass(self, feat, self.mainWindow)  # 创建属性输入窗口对象
            inputAttrWindows.exec()  # 执行属性输入窗口

    def addFeatureByDict(self, resDict: dict):
        # 根据字典添加要素方法
        if resDict:  # 如果字典非空
            feat = QgsFeature(self.editLayer.fields())  # 创建要素对象
            feat.setGeometry(self.p)  # 设置几何对象
            feat.setAttributes(list(resDict.values()))  # 设置属性值
            self.editLayer.addFeature(feat)  # 添加要素到图层
            self.canvas.refresh()  # 刷新画布
            if self.otherCanvas:  # 如果有其他画布
                self.otherCanvas.refresh()  # 刷新其他画布
            self.reset()  # 重置绘图状态
            self.mainWindow.updateShpUndoRedoButton()  # 更新撤销重做按钮状态
        else:
            self.reset()  # 重置绘图状态

    def canvasMoveEvent(self, event):
        # 处理画布移动事件
        self.cursor_point = event.mapPoint()  # 获取光标点
        if not self.is_start:  # 如果未开始绘图
            return
        self.show_polygon()  # 显示多边形

    def show_polygon(self):
        # 显示多边形方法
        if self.points:  # 如果点集合非空
            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)  # 重置橡皮筋为多边形
            first_point = self.points[0]  # 获取第一个点
            last_point = self.points[-1]  # 获取最后一个点
            if first_point and last_point:  # 如果第一个点和最后一个点存在
                self.rubberBand.addPoint(first_point, False)  # 添加第一个点到橡皮筋
                for point in self.points[1:-1]:  # 遍历中间点
                    self.rubberBand.addPoint(point, False)  # 添加中间点到橡皮筋
                if self.cursor_point:  # 如果当前光标点
                    self.rubberBand.addPoint(QgsPointXY(last_point.x(), last_point.y()), False)  # 添加最后一个点到橡皮筋
                else:
                    self.rubberBand.addPoint(QgsPointXY(last_point.x(), last_point.y()), True)  # 添加最后一个点到橡皮筋并显示
                    self.rubberBand.show()  # 显示橡皮筋
                    return
                self.rubberBand.addPoint(self.cursor_point, True)  # 添加当前光标点到橡皮筋并显示
                self.rubberBand.show()  # 显示橡皮筋

    def polygon(self):
        # 构建多边形方法
        if len(self.points) <= 2:  # 如果点数量小于等于2，无法构成多边形
            return None
        pointList = []  # 创建点列表
        for point in self.points:  # 遍历点集合
            pointList.append(QgsPointXY(point[0], point[1]))  # 将点转换为QgsPointXY对象并添加到点列表中
        return QgsGeometry.fromMultiPolygonXY([[pointList]])  # 返回多边形几何对象

    def deactivate(self):
        # 停用方法
        super(PolygonMapTool, self).deactivate()  # 调用父类的停用方法
        self.deactivated.emit()  # 发射停用信号
        self.reset()  # 重置绘图状态

