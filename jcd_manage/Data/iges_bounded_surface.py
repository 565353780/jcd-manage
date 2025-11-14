"""IGES有界曲面实体 (Type 143)"""
import numpy as np
from typing import List, Optional
from jcd_manage.Data.iges_base import IGESEntity


class IGESBoundedSurface(IGESEntity):
    """IGES有界曲面 (Type 143)
    
    有界曲面类似于裁剪曲面，但表示方法不同
    """
    
    def __init__(self):
        super().__init__()
        self.surface_type: int = 0  # 曲面表示类型
        self.boundary_type: int = 0  # 边界表示类型
        self.base_surface: Optional[IGESEntity] = None  # 基础曲面
        self.boundaries: List[IGESEntity] = []  # 边界曲线
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析有界曲面数据"""
        self._set_basic_info(entity)
        
        # Type 143 有界曲面需要引用其他实体
        try:
            pass
        except:
            pass
    
    def num_boundaries(self) -> int:
        """返回边界数量"""
        return len(self.boundaries)
    
    def __repr__(self):
        return (f"IGESBoundedSurface(base_surface={type(self.base_surface).__name__ if self.base_surface else 'None'}, "
                f"boundaries={self.num_boundaries()})")
