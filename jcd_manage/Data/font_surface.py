import struct
import numpy as np
from typing import BinaryIO, List

from jcd_manage.Data.base import BaseData
from jcd_manage.Config.types import BlockType


class FontSurface(BaseData):
    """字体面片数据"""
    
    def __init__(self):
        self.material_name: str = ""
        self.matrices: np.ndarray = np.array([])  # 形状: (2, 4, 4)
        self.matrix: np.ndarray = np.array([])  # 形状: (4, 4)
        self.outline_count: int = 0  # 轮廓数量
        self.type2: int = 0
        self.type3: int = 0
        self.type4: int = 0
        self.foreground_type: BlockType = BlockType.ANGLE
        self.background_type: BlockType = BlockType.ANGLE
        self.thickness: float = 0.0
        self.radius: float = 0.0
        self.outline_sizes: np.ndarray = np.array([])  # 每个轮廓的点数量，形状: (outline_count,)
        self.outline_unknown_data: List[bytes] = []  # 每个轮廓的未知数据
        self.points: np.ndarray = np.array([])  # 所有轮廓点，形状: (total_points, 3)
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取字体面片数据"""
        # 读取矩阵
        self.matrices = self.read_matrices(jcd_file, 2)
        
        # 读取材质
        self.material_name = self.read_string(jcd_file)
        
        # 读取单个矩阵
        self.matrix = self.read_matrix(jcd_file)
        
        # 读取各种参数
        self.outline_count = self.read_int(jcd_file)
        self.type2 = self.read_int(jcd_file)
        self.type3 = self.read_int(jcd_file)
        self.type4 = self.read_int(jcd_file)
        self.foreground_type = BlockType(self.read_int(jcd_file))
        self.background_type = BlockType(self.read_int(jcd_file))
        self.thickness = self.read_float(jcd_file)
        self.radius = self.read_float(jcd_file)
        
        # 读取轮廓大小
        self.outline_sizes = np.zeros(self.outline_count, dtype=np.int32)
        self.outline_unknown_data = []
        total_points = 0
        
        for i in range(self.outline_count):
            size = self.read_int(jcd_file)
            self.outline_sizes[i] = size
            unknown_data = jcd_file.read(4)
            self.outline_unknown_data.append(unknown_data)
            total_points += size
        
        # 读取所有轮廓点（3D点）
        if total_points > 0:
            self.points = np.zeros((total_points, 3), dtype=np.float32)
            for i in range(total_points):
                self.points[i] = struct.unpack('<fff', jcd_file.read(12))
        else:
            self.points = np.array([]).reshape(0, 3)
    
    def __repr__(self):
        return (f"FontSurface(material='{self.material_name}', "
                f"outline_count={self.outline_count}, "
                f"points_shape={self.points.shape}, "
                f"foreground_type={self.foreground_type}, "
                f"background_type={self.background_type})")
