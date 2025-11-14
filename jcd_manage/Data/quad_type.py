import numpy as np
from typing import BinaryIO

from jcd_manage.Data.base import BaseData


class QuadType(BaseData):
    """四边形面片数据"""
    
    def __init__(self):
        self.material_name: str = ""
        self.points: np.ndarray = np.array([])  # 形状: (n, 4)
        self.int_points: np.ndarray = np.array([])  # 顶点索引，形状: (n, 4)
        self.matrices: np.ndarray = np.array([])  # 形状: (2, 4, 4)
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取四边形面片数据"""
        # 读取矩阵
        self.matrices = self.read_matrices(jcd_file, 2)
        
        # 读取材质
        self.material_name = self.read_string(jcd_file)
        
        # 读取点
        self.points = self.read_points(jcd_file)
        
        # 读取顶点索引
        self.int_points = self.read_int_points(jcd_file)
    
    def __repr__(self):
        return (f"QuadType(material='{self.material_name}', "
                f"points_shape={self.points.shape}, "
                f"int_points_shape={self.int_points.shape})")
