from qgis.core import QgsApplication

# 告知QGIS路径
QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)

# 第二个参数为是否启用GUI
qgs = QgsApplication([], False)

# 初始化QGIS
qgs.initQgis()

# 开始写代码
print(QgsApplication.prefixPath())
print("Hello Qgis！")

# 从内存中删除数据提供程序和层注册表来结束
qgs.exitQgis()
