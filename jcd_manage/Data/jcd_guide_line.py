"""JCD辅助线数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData


class JCDGuideLine(JCDBaseData):
    """JCD辅助线类
    
    存储辅助线数据
    """
    
    def __init__(self):
        super().__init__()
        self.matrix: np.ndarray = np.eye(4, dtype=np.float32)  # 变换矩阵
        self.unknown_data1: bytes = b''
        self.unknown_data2: int = 0
        self.unknown_data3: int = 0
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载辅助线数据"""
        super()._load_from_dict(data)
        
        # 辅助线的matrix字段是单独的
        if 'matrix' in data and len(data['matrix']) > 0:
            self.matrix = data['matrix'][0]
        
        self.unknown_data1 = data.get('unknown_data1', b'')
        self.unknown_data2 = data.get('unknown_data2', 0)
        self.unknown_data3 = data.get('unknown_data3', 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'matrix': self.matrix.reshape(1, 4, 4),
            'unknown_data1': self.unknown_data1,
            'unknown_data2': self.unknown_data2,
            'unknown_data3': self.unknown_data3,
        })
        return data
    
    def get_position(self) -> np.ndarray:
        """从变换矩阵获取位置
        
        Returns:
            3D位置向量
        """
        return self.matrix[:3, 3]
    
    def get_direction(self) -> np.ndarray:
        """从变换矩阵获取方向（假设为Z轴方向）
        
        Returns:
            3D方向向量
        """
        direction = self.matrix[:3, 2]  # Z轴
        norm = np.linalg.norm(direction)
        if norm > 0:
            return direction / norm
        return np.array([0, 0, 1])
    
    def __repr__(self):
        return (f"JCDGuideLine(position={self.get_position()}, "
                f"direction={self.get_direction()}, "
                f"hide={self.hide})")
