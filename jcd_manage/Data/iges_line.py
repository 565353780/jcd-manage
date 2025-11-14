"""IGES直线实体 (Type 110)"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESLine(IGESEntity):
    """IGES直线 (Type 110)"""
    
    def __init__(self):
        super().__init__()
        self.start_point: np.ndarray = np.zeros(3, dtype=np.float64)
        self.end_point: np.ndarray = np.zeros(3, dtype=np.float64)
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析直线数据"""
        self._set_basic_info(entity)
        
        # 尝试从reader转换
        try:
            # IGESControl_Reader的TransferCurve可能不适用于所有曲线类型
            # 直线可能需要从原始参数中解析
            pass
        except:
            pass
    
    def length(self) -> float:
        """计算直线长度"""
        return np.linalg.norm(self.end_point - self.start_point)
    
    def direction(self) -> np.ndarray:
        """计算方向向量（单位向量）"""
        vec = self.end_point - self.start_point
        length = np.linalg.norm(vec)
        if length > 0:
            return vec / length
        return np.zeros(3)
    
    def __repr__(self):
        return (f"IGESLine(start={self.start_point}, end={self.end_point}, "
                f"length={self.length():.2f})")
