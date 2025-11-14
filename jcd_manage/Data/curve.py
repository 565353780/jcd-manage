import numpy as np
from typing import BinaryIO

from jcd_manage.Data.base import BaseData
from jcd_manage.Config.types import CurveType


class Curve(BaseData):
    """曲线数据"""
    
    def __init__(self):
        self.material_name: str = ""
        self.points: np.ndarray = np.array([])  # 形状: (n, 4)
        self.ring_count: int = 0  # 曲线数量
        self.original_point_count: int = 0  # 每条曲线的点数量
        self.curve_type: CurveType = CurveType.OPEN_CURVE
        self.matrices: np.ndarray = np.array([])  # 形状: (2, 4, 4)
        self.unknown_data: bytes = b''
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取曲线数据"""
        # 读取矩阵
        self.matrices = self.read_matrices(jcd_file, 2)
        
        # 读取材质
        self.material_name = self.read_string(jcd_file)
        
        # 读取点
        self.points = self.read_points(jcd_file)
        
        # 读取曲线数量和点数量
        self.ring_count = self.read_int(jcd_file)
        self.original_point_count = self.read_int(jcd_file)
        
        # 读取曲线类型
        self.curve_type = CurveType(self.read_byte(jcd_file))
        
        # 读取未知数据
        self.unknown_data = jcd_file.read(9)
    
    def __repr__(self):
        return (f"Curve(material='{self.material_name}', "
                f"points_shape={self.points.shape}, "
                f"ring_count={self.ring_count}, "
                f"original_point_count={self.original_point_count}, "
                f"curve_type={self.curve_type})")
