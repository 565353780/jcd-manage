"""IGES裁剪曲面实体 (Type 144)"""
import numpy as np
from typing import List, Optional
from jcd_manage.Data.iges_base import IGESEntity


class IGESTrimmedSurface(IGESEntity):
    """IGES裁剪曲面 (Type 144)
    
    裁剪曲面是由基础曲面和裁剪边界曲线定义的曲面
    """
    
    def __init__(self):
        super().__init__()
        self.base_surface: Optional[IGESEntity] = None  # 基础曲面
        self.outer_boundary: List[IGESEntity] = []  # 外边界曲线
        self.inner_boundaries: List[List[IGESEntity]] = []  # 内边界曲线（孔）
        self.n1: int = 0  # 外边界标志
        self.n2: int = 0  # 内边界数量
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析裁剪曲面数据"""
        self._set_basic_info(entity)
        
        # Type 144 裁剪曲面需要引用其他实体
        # 这需要在加载器层面处理实体之间的引用关系
        try:
            pass
        except:
            pass
    
    def has_holes(self) -> bool:
        """判断是否有内边界（孔）"""
        return len(self.inner_boundaries) > 0
    
    def num_holes(self) -> int:
        """返回孔的数量"""
        return len(self.inner_boundaries)
    
    def __repr__(self):
        return (f"IGESTrimmedSurface(base_surface={type(self.base_surface).__name__ if self.base_surface else 'None'}, "
                f"holes={self.num_holes()})")
