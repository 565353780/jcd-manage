"""IGES NURBS曲面实体 (Type 128)"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESNURBSSurface(IGESEntity):
    """IGES NURBS曲面 (Type 128)
    
    NURBS (Non-Uniform Rational B-Spline) 曲面是CAD中最常用的曲面表示方法
    """
    
    def __init__(self):
        super().__init__()
        # 基本参数
        self.u_degree: int = 0  # U方向阶数
        self.v_degree: int = 0  # V方向阶数
        
        # 控制点网格 (u_poles, v_poles, 3)
        self.control_points: np.ndarray = np.array([]).reshape(0, 0, 3)
        
        # 权重网格 (u_poles, v_poles)
        self.weights: np.ndarray = np.array([]).reshape(0, 0)
        
        # U方向节点
        self.u_knots: np.ndarray = np.array([])
        self.u_multiplicities: np.ndarray = np.array([])
        
        # V方向节点
        self.v_knots: np.ndarray = np.array([])
        self.v_multiplicities: np.ndarray = np.array([])
        
        # 属性
        self.is_u_periodic: bool = False
        self.is_v_periodic: bool = False
        self.is_rational: bool = False
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析NURBS曲面数据"""
        self._set_basic_info(entity)
        
        try:
            # 使用IGESToBRep转换器
            from OCC.Core.IGESToBRep import IGESToBRep_CurveAndSurface
            from OCC.Core.IGESGeom import IGESGeom_BSplineSurface
            
            # 检查是否为IGES BSpline曲面
            bspline_surface = IGESGeom_BSplineSurface.DownCast(entity)
            if bspline_surface:
                # 转换器
                converter = IGESToBRep_CurveAndSurface()
                converter.Init()
                
                # 转换为曲面
                surface = converter.TransferSurface(bspline_surface)
                if surface:
                    self._parse_geom_surface(surface)
        except Exception as e:
            # 如果转换失败，只保留基本信息
            pass
    
    def _parse_geom_surface(self, surface):
        """解析Geom曲面对象"""
        from OCC.Core.Geom import Geom_BSplineSurface
        
        # 检查是否为BSpline曲面
        bspline = Geom_BSplineSurface.DownCast(surface)
        if not bspline:
            return
        
        # 基本参数
        self.u_degree = bspline.UDegree()
        self.v_degree = bspline.VDegree()
        self.is_u_periodic = bspline.IsUPeriodic()
        self.is_v_periodic = bspline.IsVPeriodic()
        self.is_rational = bspline.IsURational() or bspline.IsVRational()
        
        # 控制点网格
        u_poles = bspline.NbUPoles()
        v_poles = bspline.NbVPoles()
        
        poles = np.zeros((u_poles, v_poles, 3), dtype=np.float64)
        weights = np.zeros((u_poles, v_poles), dtype=np.float64)
        
        for i in range(u_poles):
            for j in range(v_poles):
                pole = bspline.Pole(i + 1, j + 1)  # OCC索引从1开始
                poles[i, j] = self.coord_to_array(pole)
                
                if self.is_rational:
                    weights[i, j] = bspline.Weight(i + 1, j + 1)
                else:
                    weights[i, j] = 1.0
        
        self.control_points = poles
        self.weights = weights
        
        # U方向节点
        u_num_knots = bspline.NbUKnots()
        u_knots = np.zeros(u_num_knots, dtype=np.float64)
        u_mults = np.zeros(u_num_knots, dtype=np.int32)
        
        for i in range(u_num_knots):
            u_knots[i] = bspline.UKnot(i + 1)
            u_mults[i] = bspline.UMultiplicity(i + 1)
        
        self.u_knots = u_knots
        self.u_multiplicities = u_mults
        
        # V方向节点
        v_num_knots = bspline.NbVKnots()
        v_knots = np.zeros(v_num_knots, dtype=np.float64)
        v_mults = np.zeros(v_num_knots, dtype=np.int32)
        
        for i in range(v_num_knots):
            v_knots[i] = bspline.VKnot(i + 1)
            v_mults[i] = bspline.VMultiplicity(i + 1)
        
        self.v_knots = v_knots
        self.v_multiplicities = v_mults
    
    def num_u_poles(self) -> int:
        """返回U方向控制点数量"""
        return self.control_points.shape[0] if self.control_points.size > 0 else 0
    
    def num_v_poles(self) -> int:
        """返回V方向控制点数量"""
        return self.control_points.shape[1] if self.control_points.size > 0 else 0
    
    def total_poles(self) -> int:
        """返回总控制点数量"""
        return self.num_u_poles() * self.num_v_poles()
    
    def num_u_knots(self) -> int:
        """返回U方向节点数量"""
        return len(self.u_knots)
    
    def num_v_knots(self) -> int:
        """返回V方向节点数量"""
        return len(self.v_knots)
    
    def bounding_box(self) -> tuple:
        """计算控制点的边界框
        
        Returns:
            (min_point, max_point): 最小点和最大点
        """
        if self.control_points.size == 0:
            return np.zeros(3), np.zeros(3)
        
        # 将控制点网格展平为(n, 3)形状
        flat_points = self.control_points.reshape(-1, 3)
        
        min_point = np.min(flat_points, axis=0)
        max_point = np.max(flat_points, axis=0)
        
        return min_point, max_point
    
    def get_u_curve(self, v_index: int) -> np.ndarray:
        """获取指定V参数的U方向曲线控制点
        
        Args:
            v_index: V方向索引
            
        Returns:
            控制点数组 (u_poles, 3)
        """
        if 0 <= v_index < self.num_v_poles():
            return self.control_points[:, v_index, :]
        return np.array([]).reshape(0, 3)
    
    def get_v_curve(self, u_index: int) -> np.ndarray:
        """获取指定U参数的V方向曲线控制点
        
        Args:
            u_index: U方向索引
            
        Returns:
            控制点数组 (v_poles, 3)
        """
        if 0 <= u_index < self.num_u_poles():
            return self.control_points[u_index, :, :]
        return np.array([]).reshape(0, 3)
    
    def __repr__(self):
        return (f"IGESNURBSSurface(u_degree={self.u_degree}, v_degree={self.v_degree}, "
                f"u_poles={self.num_u_poles()}, v_poles={self.num_v_poles()}, "
                f"u_knots={self.num_u_knots()}, v_knots={self.num_v_knots()}, "
                f"u_periodic={self.is_u_periodic}, v_periodic={self.is_v_periodic}, "
                f"rational={self.is_rational})")
