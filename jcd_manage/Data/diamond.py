import numpy as np
from typing import BinaryIO

from jcd_manage.Data.base import BaseData
from jcd_manage.Config.types import DiamondType


class Diamond(BaseData):
    """钻石数据"""
    
    def __init__(self):
        self.material_name: str = ""
        self.matrices: np.ndarray = np.array([])  # 形状: (2, 4, 4) - 实际只有1个矩阵，但为了统一接口读取2个
        self.matrix: np.ndarray = np.array([])  # 形状: (4, 4)
        self.diamond_type: DiamondType = DiamondType.ROUND
        self.unknown_data: bytes = b''
    
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取钻石数据"""
        # 读取矩阵
        self.matrices = self.read_matrices(jcd_file, 2)
        
        # 读取材质
        self.material_name = self.read_string(jcd_file)
        
        # 读取单个矩阵（钻石特有）
        self.matrix = self.read_matrix(jcd_file)
        
        # 读取钻石类型
        self.diamond_type = DiamondType(self.read_byte(jcd_file))
        
        # 读取未知数据
        self.unknown_data = jcd_file.read(3)
    
    def __repr__(self):
        return (f"Diamond(material='{self.material_name}', "
                f"diamond_type={self.diamond_type})")
