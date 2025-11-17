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
        
        try:
            # 使用IGESToBRep转换器
            from OCC.Core.IGESToBRep import IGESToBRep_CurveAndSurface
            from OCC.Core.IGESGeom import IGESGeom_Line
            
            # 检查是否为IGES Line
            line = IGESGeom_Line.DownCast(entity)
            if line:
                # 转换器
                converter = IGESToBRep_CurveAndSurface()
                converter.Init()
                
                # 转换为曲线
                curve = converter.TransferCurve(line)
                if curve:
                    self._parse_geom_line(curve)
        except Exception as e:
            # 如果转换失败，只保留基本信息
            pass
    
    def _parse_geom_line(self, curve):
        """解析Geom直线对象"""
        from OCC.Core.Geom import Geom_Line
        
        # 检查是否为Line
        line = Geom_Line.DownCast(curve)
        if not line:
            return
        
        # 获取起点和方向
        location = line.Location()
        direction = line.Direction()
        
        self.start_point = self.coord_to_array(location)
        dir_vec = np.array([direction.X(), direction.Y(), direction.Z()], dtype=np.float64)
        
        # 计算终点（假设参数范围）
        # 注意：IGES直线可能是无限长的，这里只设置一个合理的长度
        length = 100.0  # 默认长度
        self.end_point = self.start_point + dir_vec * length
    
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
