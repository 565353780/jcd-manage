"""JCD钻石数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import DiamondType


class JCDDiamond(JCDBaseData):
    """JCD钻石类
    
    存储钻石数据，包括钻石类型、材质、变换矩阵等
    """
    
    def __init__(self):
        super().__init__()
        self.material_name: str = ""
        self.matrix: np.ndarray = np.eye(4, dtype=np.float32)  # 单个变换矩阵
        self.diamond_type: Optional[DiamondType] = None
        self.unknown_data: bytes = b''
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载钻石数据"""
        super()._load_from_dict(data)
        self.material_name = data.get('material_name', '')
        
        # 钻石的matrix字段是单独的，不同于matrices
        if 'matrix' in data and len(data['matrix']) > 0:
            self.matrix = data['matrix'][0]  # 取第一个矩阵

        self.diamond_type = data.get('diamond_type')
        self.unknown_data = data.get('unknown_data', b'')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'material_name': self.material_name,
            'matrix': self.matrix.reshape(1, 4, 4),  # 保持一致的格式
            'diamond_type': self.diamond_type,
            'unknown_data': self.unknown_data,
        })
        return data

    def get_position(self) -> np.ndarray:
        """从变换矩阵获取位置

        Returns:
            3D位置向量
        """
        return self.matrix[3, :3]

    def get_diamond_type_name(self) -> str:
        """获取钻石类型名称"""
        if self.diamond_type is None:
            return "Unknown"
        
        type_names = {
            DiamondType.ROUND: "圆形",
            DiamondType.MARQUISE: "马眼",
            DiamondType.PEAR: "梨形",
            DiamondType.HEART: "心形",
            DiamondType.OCTAGON: "八方",
            DiamondType.SQUARE: "方形",
            DiamondType.TRIANGLE: "三角",
        }
        return type_names.get(self.diamond_type, str(self.diamond_type))

    def get_points(self) -> Optional[np.ndarray]:
        """获取钻石的中心点（用于可视化）

        Returns:
            中心点数组 (1, 3)
        """
        # 钻石用位置作为其"点"
        position = self.get_position()
        return position.reshape(1, 3)

    def get_transform_matrix(self) -> np.ndarray:
        """获取完整的变换矩阵（包括自身matrix和继承的matrices）

        Returns:
            4x4变换矩阵
        """
        # 从自身的matrix开始
        result = self.matrix.copy()

        # 应用继承自基类的所有变换矩阵
        for matrix in self.matrices:
            result = matrix @ result

        return result

    def __repr__(self):
        return (f"JCDDiamond(material='{self.material_name}', "
                f"type={self.get_diamond_type_name()}, "
                f"position={self.get_position()}, "
                f"hide={self.hide})")
