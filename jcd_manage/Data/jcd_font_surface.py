"""JCD字体面片数据类"""
import numpy as np
from typing import Dict, Any, Optional, List
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import BlockType


class JCDFontSurface(JCDBaseData):
    """JCD字体面片类
    
    存储字体面片数据，包括轮廓、前景/背景类型等
    """
    
    def __init__(self):
        super().__init__()
        self.material_name: str = ""
        self.matrix: np.ndarray = np.eye(4, dtype=np.float32)  # 变换矩阵
        self.outline_count: int = 0  # 轮廓数量
        self.type2: int = 0
        self.type3: int = 0
        self.type4: int = 0
        self.foreground_type: Optional[BlockType] = None  # 前景类型
        self.background_type: Optional[BlockType] = None  # 背景类型
        self.thickness: float = 0.0  # 厚度
        self.radius: float = 0.0  # 半径
        self.outline_sizes: np.ndarray = np.array([], dtype=np.int32)  # 每个轮廓的点数
        self.points: np.ndarray = np.array([]).reshape(0, 3)  # 所有轮廓点 (n, 3)
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载字体面片数据"""
        super()._load_from_dict(data)
        self.material_name = data.get('material_name', '')
        
        # 字体面片的matrix字段是单独的
        if 'matrix' in data and len(data['matrix']) > 0:
            self.matrix = data['matrix'][0]
        
        self.outline_count = data.get('outline_count', 0)
        self.type2 = data.get('type2', 0)
        self.type3 = data.get('type3', 0)
        self.type4 = data.get('type4', 0)
        self.foreground_type = data.get('foreground_type')
        self.background_type = data.get('background_type')
        self.thickness = data.get('thickness', 0.0)
        self.radius = data.get('radius', 0.0)
        self.outline_sizes = data.get('outline_sizes', np.array([], dtype=np.int32))
        self.points = data.get('points', np.array([]).reshape(0, 3))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'material_name': self.material_name,
            'matrix': self.matrix.reshape(1, 4, 4),
            'outline_count': self.outline_count,
            'type2': self.type2,
            'type3': self.type3,
            'type4': self.type4,
            'foreground_type': self.foreground_type,
            'background_type': self.background_type,
            'thickness': self.thickness,
            'radius': self.radius,
            'outline_sizes': self.outline_sizes,
            'points': self.points,
        })
        return data
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算所有轮廓点的边界框"""
        if len(self.points) == 0:
            return None
        
        min_point = np.min(self.points, axis=0)
        max_point = np.max(self.points, axis=0)
        return min_point, max_point
    
    def get_outline(self, index: int) -> Optional[np.ndarray]:
        """获取指定索引的轮廓点
        
        Args:
            index: 轮廓索引（0到outline_count-1）
            
        Returns:
            轮廓点数组或None
        """
        if index < 0 or index >= self.outline_count:
            return None
        
        if len(self.outline_sizes) == 0:
            return None
        
        # 计算起始位置
        start_idx = np.sum(self.outline_sizes[:index]).astype(int)
        end_idx = start_idx + self.outline_sizes[index]
        
        if end_idx > len(self.points):
            return None
        
        return self.points[start_idx:end_idx]
    
    def get_all_outlines(self) -> List[np.ndarray]:
        """获取所有轮廓
        
        Returns:
            轮廓点数组列表
        """
        outlines = []
        for i in range(self.outline_count):
            outline = self.get_outline(i)
            if outline is not None:
                outlines.append(outline)
        return outlines
    
    def total_points(self) -> int:
        """返回总点数"""
        return len(self.points)
    
    def get_foreground_type_name(self) -> str:
        """获取前景类型名称"""
        if self.foreground_type is None:
            return "Unknown"
        
        type_names = {
            BlockType.ANGLE: "尖角",
            BlockType.ROUND: "圆角",
            BlockType.CUT: "切角",
        }
        return type_names.get(self.foreground_type, str(self.foreground_type))
    
    def get_background_type_name(self) -> str:
        """获取背景类型名称"""
        if self.background_type is None:
            return "Unknown"
        
        type_names = {
            BlockType.ANGLE: "尖角",
            BlockType.ROUND: "圆角",
            BlockType.CUT: "切角",
        }
        return type_names.get(self.background_type, str(self.background_type))
    
    def transform_points(self, matrix: np.ndarray):
        """变换所有轮廓点
        
        Args:
            matrix: 4x4变换矩阵
        """
        if len(self.points) == 0:
            return
        
        # 转换为齐次坐标
        homogeneous = np.hstack([self.points, np.ones((len(self.points), 1))])
        
        # 应用变换
        transformed = (matrix @ homogeneous.T).T
        
        # 转回3D坐标
        self.points = transformed[:, :3]
    
    def get_points(self) -> Optional[np.ndarray]:
        """获取原始点数据
        
        Returns:
            点数组 (n, 3)
        """
        if len(self.points) == 0:
            return None
        return self.points
    
    def get_transformed_points(self) -> Optional[np.ndarray]:
        """获取应用变换后的点数据（包括自身matrix和继承的matrices）
        
        Returns:
            变换后的点数组 (n, 3) 或 None
        """
        points = self.get_points()
        if points is None or len(points) == 0:
            return None
        
        # 转换为齐次坐标
        homogeneous = np.hstack([points, np.ones((len(points), 1))])
        
        # 先应用自身的matrix
        transformed = (self.matrix @ homogeneous.T).T
        
        # 再应用继承自基类的所有变换矩阵
        for matrix in self.matrices:
            transformed = (matrix @ transformed.T).T
        
        # 返回3D坐标
        return transformed[:, :3]
    
    def __repr__(self):
        return (f"JCDFontSurface(material='{self.material_name}', "
                f"outlines={self.outline_count}, "
                f"total_points={self.total_points()}, "
                f"foreground={self.get_foreground_type_name()}, "
                f"background={self.get_background_type_name()}, "
                f"thickness={self.thickness:.2f}, "
                f"hide={self.hide})")
