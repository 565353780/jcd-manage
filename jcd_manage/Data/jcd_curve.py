"""JCD曲线数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import CurveType


class JCDCurve(JCDBaseData):
    """JCD曲线类
    
    存储曲线数据，包括控制点、材质、曲线类型等
    """
    
    def __init__(self):
        super().__init__()
        self.material_name: str = ""
        self.points: np.ndarray = np.array([]).reshape(0, 4)  # (n, 4) 控制点
        self.ring_count: int = 0  # 曲线数量
        self.original_point_count: int = 0  # 每条曲线的点数
        self.curve_type: Optional[CurveType] = None  # 曲线类型（开放/闭合）
        self.unknown_data: bytes = b''
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载曲线数据"""
        super()._load_from_dict(data)
        self.material_name = data.get('material_name', '')
        self.points = data.get('points', np.array([]).reshape(0, 4))
        self.ring_count = data.get('ring_count', 0)
        self.original_point_count = data.get('original_point_count', 0)
        self.curve_type = data.get('curve_type')
        self.unknown_data = data.get('unknown_data', b'')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'material_name': self.material_name,
            'points': self.points,
            'ring_count': self.ring_count,
            'original_point_count': self.original_point_count,
            'curve_type': self.curve_type,
            'unknown_data': self.unknown_data,
        })
        return data
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算控制点的边界框"""
        if len(self.points) == 0:
            return None
        
        min_point = np.min(self.points[:, :3], axis=0)
        max_point = np.max(self.points[:, :3], axis=0)
        return min_point, max_point
    
    def get_curve_by_index(self, index: int) -> Optional[np.ndarray]:
        """获取指定索引的曲线控制点
        
        Args:
            index: 曲线索引（0到ring_count-1）
            
        Returns:
            控制点数组或None
        """
        if index < 0 or index >= self.ring_count:
            return None
        
        if self.original_point_count == 0:
            return None
        
        start_idx = index * self.original_point_count
        end_idx = start_idx + self.original_point_count
        
        if end_idx > len(self.points):
            return None
        
        return self.points[start_idx:end_idx]
    
    def get_all_curves(self) -> list:
        """获取所有曲线
        
        Returns:
            曲线控制点列表
        """
        curves = []
        for i in range(self.ring_count):
            curve = self.get_curve_by_index(i)
            if curve is not None:
                curves.append(curve)
        return curves
    
    def is_closed(self) -> bool:
        """判断是否为闭合曲线"""
        return self.curve_type == CurveType.CLOSED_CURVE
    
    def total_points(self) -> int:
        """返回总点数"""
        return len(self.points)
    
    def transform_points(self, matrix: np.ndarray):
        """变换所有控制点
        
        Args:
            matrix: 4x4变换矩阵
        """
        if len(self.points) == 0:
            return
        
        # 应用齐次坐标变换
        transformed = (matrix @ self.points.T).T
        self.points = transformed
    
    def get_points(self) -> Optional[np.ndarray]:
        """获取原始点数据
        
        Returns:
            点数组 (n, 3)
        """
        if len(self.points) == 0:
            return None
        return self.points[:, :3]
    
    def __repr__(self):
        return (f"JCDCurve(material='{self.material_name}', "
                f"curves={self.ring_count}, "
                f"points_per_curve={self.original_point_count}, "
                f"total_points={self.total_points()}, "
                f"type={self.curve_type}, "
                f"hide={self.hide})")
