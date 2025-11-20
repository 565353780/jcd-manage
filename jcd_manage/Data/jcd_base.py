"""JCD数据基类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Config.types import SurfaceType


class JCDBaseData:
    """JCD数据基类
    
    所有JCD实体类型的基类，提供通用的数据存储和访问方法
    """
    
    def __init__(self):
        """初始化基础属性"""
        self.surface_type: Optional[SurfaceType] = None
        self.matrices: np.ndarray = np.array([]).reshape(0, 4, 4)  # 变换矩阵
        self.meta_info: bytes = b''  # 元信息
        self.hide: bool = False  # 是否隐藏
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建实例
        
        Args:
            data: 包含实体数据的字典
            
        Returns:
            实例对象
        """
        instance = cls()
        instance._load_from_dict(data)
        return instance
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载数据（子类可重写此方法）
        
        Args:
            data: 包含实体数据的字典
        """
        self.surface_type = data.get('surface_type')
        self.matrices = data.get('matrices', np.array([]).reshape(0, 4, 4))
        self.meta_info = data.get('meta_info', b'')
        self.hide = data.get('hide', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）
        
        Returns:
            包含实体数据的字典
        """
        return {
            'surface_type': self.surface_type,
            'matrices': self.matrices,
            'meta_info': self.meta_info,
            'hide': self.hide,
        }
    
    def get_bounding_box(self) -> Optional[tuple]:
        """获取边界框（子类应重写此方法）
        
        Returns:
            (min_point, max_point) 或 None
        """
        return None
    
    def transform(self, matrix: np.ndarray):
        """应用变换矩阵（子类可重写以变换控制点）
        
        Args:
            matrix: 4x4变换矩阵
        """
        # 默认实现：将矩阵添加到变换链中
        if len(self.matrices) > 0:
            # 如果已有矩阵，进行矩阵乘法
            transformed_matrices = np.zeros_like(self.matrices)
            for i, m in enumerate(self.matrices):
                transformed_matrices[i] = matrix @ m
            self.matrices = transformed_matrices
        else:
            self.matrices = matrix.reshape(1, 4, 4)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.surface_type}, hide={self.hide})"
