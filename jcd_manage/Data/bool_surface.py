import numpy as np
from typing import BinaryIO, Optional

from jcd_manage.Data.base import BaseData
from jcd_manage.Config.types import BoolType, SurfaceType


class BoolSurface(BaseData):
    """布尔曲面数据"""
    
    def __init__(self):
        self.matrices: np.ndarray = np.array([])  # 形状: (3, 4, 4)
        self.bool_type: BoolType = BoolType.UNION
        self.unknown_data1: bytes = b''
        self.surface_type: SurfaceType = SurfaceType.SURFACE
        self.unknown_data2: bytes = b''
        self.child_surface: Optional[BaseData] = None  # 嵌套的曲面对象
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取布尔曲面数据"""
        # 读取矩阵
        self.matrices = self.read_matrices(jcd_file, 3)
        
        # 读取布尔类型
        self.bool_type = BoolType(self.read_byte(jcd_file))
        
        # 读取未知数据
        self.unknown_data1 = jcd_file.read(2)
        
        # 读取内部曲面类型
        self.surface_type = SurfaceType(self.read_byte(jcd_file))
        
        # 读取未知数据
        self.unknown_data2 = jcd_file.read(7)
        
        # 根据类型读取嵌套的曲面数据
        # 注意：这里不读取嵌套的矩阵，因为已经在read_by_surface_type中处理
        self.child_surface = self._create_child_surface(self.surface_type)
        if self.child_surface:
            # 嵌套曲面需要从read_by_surface_type调用，这里只是占位
            # 实际读取由外部控制
            pass
    
    def _create_child_surface(self, surface_type: SurfaceType) -> Optional[BaseData]:
        """根据类型创建子曲面对象"""
        from jcd_manage.Data.curve import Curve
        from jcd_manage.Data.surface import Surface
        from jcd_manage.Data.diamond import Diamond
        from jcd_manage.Data.font_surface import FontSurface
        from jcd_manage.Data.guide_line import GuideLine
        from jcd_manage.Data.quad_type import QuadType
        
        if surface_type == SurfaceType.CURVE:
            return Curve()
        elif surface_type == SurfaceType.SURFACE:
            return Surface()
        elif surface_type == SurfaceType.BOOL_SURFACE:
            return BoolSurface()
        elif surface_type == SurfaceType.DIAMOND:
            return Diamond()
        elif surface_type == SurfaceType.FONT_SURFACE:
            return FontSurface()
        elif surface_type == SurfaceType.GUIDE_LINE:
            return GuideLine()
        elif surface_type == SurfaceType.QUAD_TYPE:
            return QuadType()
        return None
    
    def __repr__(self):
        return (f"BoolSurface(bool_type={self.bool_type}, "
                f"surface_type={self.surface_type}, "
                f"child={type(self.child_surface).__name__ if self.child_surface else 'None'})")
