"""IGES圆弧实体 (Type 100)"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESCircularArc(IGESEntity):
    """IGES圆弧 (Type 100)"""
    
    def __init__(self):
        super().__init__()
        self.center: np.ndarray = np.zeros(3, dtype=np.float64)
        self.start_point: np.ndarray = np.zeros(3, dtype=np.float64)
        self.end_point: np.ndarray = np.zeros(3, dtype=np.float64)
        self.radius: float = 0.0
        self.normal: np.ndarray = np.array([0, 0, 1], dtype=np.float64)  # 默认Z轴
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析圆弧数据"""
        self._set_basic_info(entity)
        
        # 圆弧数据通常需要从原始参数中解析
        # IGES 100类型的参数格式：ZT, X1, Y1, X2, Y2, X3, Y3
        # 其中 (X1,Y1)是中心, (X2,Y2)是起点, (X3,Y3)是终点
        try:
            pass
        except:
            pass
    
    def arc_angle(self) -> float:
        """计算圆弧角度（弧度）"""
        v1 = self.start_point - self.center
        v2 = self.end_point - self.center
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.arccos(cos_angle)
    
    def arc_length(self) -> float:
        """计算圆弧长度"""
        return self.radius * self.arc_angle()
    
    def __repr__(self):
        return (f"IGESCircularArc(center={self.center}, radius={self.radius:.2f}, "
                f"angle={np.degrees(self.arc_angle()):.1f}°)")
