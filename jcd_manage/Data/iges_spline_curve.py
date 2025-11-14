"""IGES参数样条曲线实体 (Type 112)"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESSplineCurve(IGESEntity):
    """IGES参数样条曲线 (Type 112)"""
    
    def __init__(self):
        super().__init__()
        self.degree: int = 0
        self.segments: int = 0
        self.control_points: np.ndarray = np.array([]).reshape(0, 3)
        self.break_points: np.ndarray = np.array([])
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析样条曲线数据"""
        self._set_basic_info(entity)
        
        # Type 112 参数样条曲线需要从原始参数解析
        try:
            pass
        except:
            pass
    
    def __repr__(self):
        return (f"IGESSplineCurve(degree={self.degree}, segments={self.segments}, "
                f"points={len(self.control_points)})")
