"""JCD布尔曲面数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import BoolType, SurfaceType


class JCDBoolSurface(JCDBaseData):
    """JCD布尔曲面类
    
    存储布尔操作的曲面数据，包含子曲面
    """
    
    def __init__(self):
        super().__init__()
        self.bool_type: Optional[BoolType] = None  # 布尔操作类型
        self.unknown_data1: bytes = b''
        self.sub_surface_type: Optional[SurfaceType] = None  # 子曲面类型
        self.unknown_data2: bytes = b''
        self.sub_surface: Optional[Dict[str, Any]] = None  # 子曲面数据
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载布尔曲面数据"""
        super()._load_from_dict(data)
        self.bool_type = data.get('bool_type')
        self.unknown_data1 = data.get('unknown_data1', b'')
        
        # 子曲面数据
        if 'sub_surface' in data:
            self.sub_surface = data['sub_surface']
            self.sub_surface_type = self.sub_surface.get('surface_type')
        else:
            self.sub_surface_type = data.get('surface_type')
        
        self.unknown_data2 = data.get('unknown_data2', b'')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'bool_type': self.bool_type,
            'unknown_data1': self.unknown_data1,
            'sub_surface_type': self.sub_surface_type,
            'unknown_data2': self.unknown_data2,
            'sub_surface': self.sub_surface,
        })
        return data
    
    def get_bool_type_name(self) -> str:
        """获取布尔操作类型名称"""
        if self.bool_type is None:
            return "Unknown"
        
        type_names = {
            BoolType.UNION: "并集",
            BoolType.INTERSECTION: "交集",
            BoolType.DIFFERENCE: "差集",
        }
        return type_names.get(self.bool_type, str(self.bool_type))
    
    def has_sub_surface(self) -> bool:
        """检查是否有子曲面数据"""
        return self.sub_surface is not None and len(self.sub_surface) > 0
    
    def get_sub_surface_points(self) -> Optional[np.ndarray]:
        """获取子曲面的点数据
        
        Returns:
            点数组或None
        """
        if not self.has_sub_surface():
            return None
        
        return self.sub_surface.get('points')
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算子曲面的边界框"""
        points = self.get_sub_surface_points()
        if points is None or len(points) == 0:
            return None
        
        min_point = np.min(points[:, :3], axis=0)
        max_point = np.max(points[:, :3], axis=0)
        return min_point, max_point
    
    def get_points(self) -> Optional[np.ndarray]:
        """获取子曲面的原始点数据
        
        Returns:
            点数组 (n, 3) 或 None
        """
        points = self.get_sub_surface_points()
        if points is None or len(points) == 0:
            return None
        return points[:, :3]
    
    def __repr__(self):
        sub_type = self.sub_surface_type if self.sub_surface_type else "None"
        return (f"JCDBoolSurface(bool_type={self.get_bool_type_name()}, "
                f"sub_surface_type={sub_type}, "
                f"hide={self.hide})")
