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
        
        try:
            # 使用IGESToBRep转换器
            from OCC.Core.IGESToBRep import IGESToBRep_CurveAndSurface
            from OCC.Core.IGESGeom import IGESGeom_CircularArc
            
            # 检查是否为IGES CircularArc
            arc = IGESGeom_CircularArc.DownCast(entity)
            if arc:
                # 转换器
                converter = IGESToBRep_CurveAndSurface()
                converter.Init()
                
                # 转换为曲线
                curve = converter.TransferCurve(arc)
                if curve:
                    self._parse_geom_circle(curve)
        except Exception as e:
            # 如果转换失败，只保留基本信息
            pass
    
    def _parse_geom_circle(self, curve):
        """解析Geom圆/圆弧对象"""
        from OCC.Core.Geom import Geom_Circle, Geom_TrimmedCurve
        
        # 可能是TrimmedCurve（裁剪后的圆）
        trimmed = Geom_TrimmedCurve.DownCast(curve)
        if trimmed:
            basis_curve = trimmed.BasisCurve()
            circle = Geom_Circle.DownCast(basis_curve)
            if circle:
                self._extract_circle_data(circle)
            return
        
        # 或者直接是Circle
        circle = Geom_Circle.DownCast(curve)
        if circle:
            self._extract_circle_data(circle)
    
    def _extract_circle_data(self, circle):
        """提取圆的基本数据"""
        # 获取圆的位置和轴
        position = circle.Position()
        location = position.Location()
        axis = position.Axis()
        
        self.center = self.coord_to_array(location)
        self.normal = np.array([axis.Direction().X(), axis.Direction().Y(), axis.Direction().Z()], dtype=np.float64)
        self.radius = circle.Radius()
    
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
