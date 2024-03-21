import os  # 导入 os 模块，用于操作文件系统
import os.path as osp  # 导入 os.path 模块并重命名为 osp，用于处理文件路径

def getFileSize(filePath):
    # 定义函数 getFileSize，用于获取文件大小信息
    fsize = osp.getsize(filePath)  # 使用 osp.getsize() 函数获取文件大小，返回的是字节大小

    if fsize < 1024:
        # 如果文件大小小于 1024 字节，则直接返回文件大小并添加单位 Byte
        return f"{round(fsize, 2)}Byte"
    else:
        KBX = fsize / 1024  # 将文件大小转换为 KB 单位
        if KBX < 1024:
            # 如果文件大小小于 1024 KB，则返回文件大小并添加单位 Kb
            return f"{round(KBX, 2)}Kb"
        else:
            MBX = KBX / 1024  # 将文件大小转换为 MB 单位
            if MBX < 1024:
                # 如果文件大小小于 1024 MB，则返回文件大小并添加单位 Mb
                return f"{round(MBX, 2)}Mb"
            else:
                # 如果文件大小大于等于 1024 MB，则返回文件大小并添加单位 Gb
                return f"{round(MBX/1024,2)}Gb"
