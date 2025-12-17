"""JCD曲面数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import CurveType


class JCDSurface(JCDBaseData):
    """JCD曲面类
    
    存储曲面数据，包括控制点网格、材质等
    """
    
    def __init__(self):
        super().__init__()
        self.material_name: str = ""
        self.points: np.ndarray = np.array([]).reshape(0, 4)  # (n, 4) 控制点
        self.ring_count: int = 0  # U方向曲线数量
        self.original_point_count: int = 0  # V方向点数
        self.curve_type: Optional[CurveType] = None
        self.is_path_closed: bool = False
        self.is_cross_section_closed: bool = False
        self.normal_direction: int = 1
        self.unknown_data: bytes = b''
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载曲面数据"""
        super()._load_from_dict(data)
        self.material_name = data.get('material_name', '')
        self.points = data.get('points', np.array([]).reshape(0, 4))
        self.ring_count = data.get('ring_count', 0)
        self.original_point_count = data.get('original_point_count', 0)
        self.curve_type = data.get('curve_type')
        self.is_path_closed = data.get('is_path_closed', False)
        self.is_cross_section_closed = data.get('is_cross_section_closed', False)
        self.normal_direction = data.get('normal_direction', 1)
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
            'is_path_closed': self.is_path_closed,
            'is_cross_section_closed': self.is_cross_section_closed,
            'normal_direction': self.normal_direction,
        })
        return data
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算控制点的边界框"""
        if len(self.points) == 0:
            return None
        
        min_point = np.min(self.points[:, :3], axis=0)
        max_point = np.max(self.points[:, :3], axis=0)
        return min_point, max_point
    
    def get_control_point_grid(self) -> Optional[np.ndarray]:
        """获取控制点网格
        
        Returns:
            形状为 (ring_count, original_point_count, 4) 的数组，或None
        """
        if self.ring_count == 0 or self.original_point_count == 0:
            return None
        
        total_points = self.ring_count * self.original_point_count
        if len(self.points) != total_points:
            return None
        
        # 重塑为网格
        return self.points.reshape(self.ring_count, self.original_point_count, 4)
    
    def get_u_curve(self, u_index: int) -> Optional[np.ndarray]:
        """获取U方向的曲线（固定U参数）
        
        Args:
            u_index: U方向索引（0到ring_count-1）
            
        Returns:
            控制点数组或None
        """
        grid = self.get_control_point_grid()
        if grid is None or u_index < 0 or u_index >= self.ring_count:
            return None
        
        return grid[u_index, :, :]
    
    def get_v_curve(self, v_index: int) -> Optional[np.ndarray]:
        """获取V方向的曲线（固定V参数）
        
        Args:
            v_index: V方向索引（0到original_point_count-1）
            
        Returns:
            控制点数组或None
        """
        grid = self.get_control_point_grid()
        if grid is None or v_index < 0 or v_index >= self.original_point_count:
            return None
        
        return grid[:, v_index, :]
    
    def total_points(self) -> int:
        """返回总点数"""
        return len(self.points)
    
    def u_count(self) -> int:
        """返回U方向曲线数量"""
        return self.ring_count
    
    def v_count(self) -> int:
        """返回V方向点数"""
        return self.original_point_count
    
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
        return (f"JCDSurface(material='{self.material_name}', "
                f"u_count={self.ring_count}, "
                f"v_count={self.original_point_count}, "
                f"total_points={self.total_points()}, "
                f"type={self.curve_type}, "
                f"hide={self.hide})")
