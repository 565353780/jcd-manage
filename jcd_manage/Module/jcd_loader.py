import os
import numpy as np
from typing import Union, List, BinaryIO

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
from jcd_manage.Data import (
    BaseData, Curve, Surface, Diamond, FontSurface, 
    GuideLine, BoolSurface, QuadType
)

class JCDLoader(object):
    def __init__(self, jcd_file_path: Union[str, None]=None) -> None:
        self.file_size = -1
        self.objects: List[BaseData] = []

        if jcd_file_path is not None:
            self.loadJCDFile(jcd_file_path)
        return

    def loadJCDFile(self, jcd_file_path: str) -> bool:
        if not os.path.exists(jcd_file_path):
            print('[ERROR][JCDLoader::loadTXTFile]')
            print('\t jcd file not exist!')
            print('\t jcd_file_path:', jcd_file_path)
            return False

        self.file_size = os.path.getsize(jcd_file_path)

        with open(jcd_file_path, 'rb') as jcd_file:
            # 验证文件头
            if not self._validate_header(jcd_file):
                print("[ERROR][JCDLoader::loadJCDFile]")
                print("\t Invalid JCD file header")
                return False

            # 读取所有对象
            while True:
                end_flag = jcd_file.read(1)

                # 检查是否到达文件末尾
                if not end_flag or jcd_file.tell() >= self.file_size:
                    break

                # 读取对象类型
                try:
                    surface_type = SurfaceType(int.from_bytes(end_flag, 'little'))
                except ValueError:
                    print(f"Unknown surface type: {int.from_bytes(end_flag, 'little')}")
                    break

                # 跳过7字节未知数据
                unknown_data = jcd_file.read(7)

                # 创建并读取对象
                obj = self._read_object_by_type(jcd_file, surface_type)
                if obj:
                    self.objects.append(obj)
                    print(f"Read object: {obj}")
        
        return self.objects
    
    def _validate_header(self, jcd_file: BinaryIO) -> bool:
        """验证JCD文件头"""
        header = jcd_file.read(len(JCD_HEADER)).decode('utf-8')
        if header != JCD_HEADER:
            print(f'Header error: {header}')
            return False
        return True
    
    def _read_object_by_type(self, jcd_file: BinaryIO, surface_type: SurfaceType) -> BaseData:
        """根据类型读取对象"""
        obj = None
        
        if surface_type == SurfaceType.CURVE:
            obj = Curve()
        elif surface_type == SurfaceType.SURFACE:
            obj = Surface()
        elif surface_type == SurfaceType.BOOL_SURFACE:
            obj = BoolSurface()
        elif surface_type == SurfaceType.DIAMOND:
            obj = Diamond()
        elif surface_type == SurfaceType.FONT_SURFACE:
            obj = FontSurface()
        elif surface_type == SurfaceType.GUIDE_LINE:
            obj = GuideLine()
        elif surface_type == SurfaceType.QUAD_TYPE:
            obj = QuadType()
        
        if obj:
            obj.from_stream(jcd_file)
            
            # 处理布尔曲面的嵌套对象
            if isinstance(obj, BoolSurface) and obj.child_surface:
                obj.child_surface.from_stream(jcd_file)
        
        return obj
