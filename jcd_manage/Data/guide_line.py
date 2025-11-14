import numpy as np
from typing import BinaryIO

from jcd_manage.Data.base import BaseData


class GuideLine(BaseData):
    """辅助线数据"""
    
    def __init__(self):
        self.matrices: np.ndarray = np.array([])  # 形状: (1, 4, 4)
        self.matrix: np.ndarray = np.array([])  # 形状: (4, 4)
        self.unknown_data1: bytes = b''
        self.unknown_data2: int = 0
        self.unknown_data3: int = 0
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取辅助线数据"""
        # 读取矩阵（辅助线只有1个矩阵）
        self.matrices = self.read_matrices(jcd_file, 1)
        self.matrix = self.matrices[0] if len(self.matrices) > 0 else np.array([])
        
        # 读取矩阵后还有一个矩阵
        self.matrix = self.read_matrix(jcd_file)
        
        # 读取未知数据
        self.unknown_data1 = jcd_file.read(4)
        self.unknown_data2 = self.read_int(jcd_file)
        self.unknown_data3 = self.read_int(jcd_file)
    
    def __repr__(self):
        return f"GuideLine(matrix_shape={self.matrix.shape})"
