"""IGES NURBS曲线实体 (Type 126)"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESNURBSCurve(IGESEntity):
    """IGES NURBS曲线 (Type 126)
    
    NURBS (Non-Uniform Rational B-Spline) 曲线是CAD中最常用的曲线表示方法
    """
    
    def __init__(self):
        super().__init__()
        self.degree: int = 0  # 曲线阶数
        self.control_points: np.ndarray = np.array([]).reshape(0, 3)  # 控制点 (n, 3)
        self.weights: np.ndarray = np.array([])  # 权重 (n,)
        self.knots: np.ndarray = np.array([])  # 节点向量
        self.multiplicities: np.ndarray = np.array([])  # 节点重复度
        self.is_periodic: bool = False  # 是否为周期曲线
        self.is_rational: bool = False  # 是否为有理曲线
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析NURBS曲线数据"""
        self._set_basic_info(entity)
        
        try:
            # 使用IGESToBRep转换器
            from OCC.Core.IGESToBRep import IGESToBRep_CurveAndSurface
            from OCC.Core.IGESGeom import IGESGeom_BSplineCurve
            from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
            from OCC.Core.TopoDS import topods_Edge
            from OCC.Core.TopAbs import TopAbs_EDGE
            from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
            
            # 检查是否为IGES BSpline曲线
            bspline_curve = IGESGeom_BSplineCurve.DownCast(entity)
            if bspline_curve:
                # 转换器
                converter = IGESToBRep_CurveAndSurface()
                converter.Init()
                
                # 转换为曲线
                curve = converter.TransferCurve(bspline_curve)
                if curve:
                    self._parse_geom_curve(curve)
        except Exception as e:
            # 如果转换失败，只保留基本信息
            pass
    
    def _parse_geom_curve(self, curve):
        """解析Geom曲线对象"""
        from OCC.Core.Geom import Geom_BSplineCurve
        
        # 检查是否为BSpline曲线
        bspline = Geom_BSplineCurve.DownCast(curve)
        if not bspline:
            return
        
        # 基本参数
        self.degree = bspline.Degree()
        self.is_periodic = bspline.IsPeriodic()
        self.is_rational = bspline.IsRational()
        
        # 控制点
        num_poles = bspline.NbPoles()
        poles = np.zeros((num_poles, 3), dtype=np.float64)
        weights = np.zeros(num_poles, dtype=np.float64)
        
        for i in range(num_poles):
            pole = bspline.Pole(i + 1)  # OCC索引从1开始
            poles[i] = self.coord_to_array(pole)
            
            if self.is_rational:
                weights[i] = bspline.Weight(i + 1)
            else:
                weights[i] = 1.0
        
        self.control_points = poles
        self.weights = weights
        
        # 节点向量
        num_knots = bspline.NbKnots()
        knots = np.zeros(num_knots, dtype=np.float64)
        mults = np.zeros(num_knots, dtype=np.int32)
        
        for i in range(num_knots):
            knots[i] = bspline.Knot(i + 1)
            mults[i] = bspline.Multiplicity(i + 1)
        
        self.knots = knots
        self.multiplicities = mults
    
    def num_control_points(self) -> int:
        """返回控制点数量"""
        return len(self.control_points)
    
    def num_knots(self) -> int:
        """返回节点数量"""
        return len(self.knots)
    
    def is_closed(self) -> bool:
        """判断曲线是否闭合"""
        if len(self.control_points) < 2:
            return False
        
        # 检查首尾控制点是否重合
        return np.allclose(self.control_points[0], self.control_points[-1])
    
    def bounding_box(self) -> tuple:
        """计算控制点的边界框
        
        Returns:
            (min_point, max_point): 最小点和最大点
        """
        if len(self.control_points) == 0:
            return np.zeros(3), np.zeros(3)
        
        min_point = np.min(self.control_points, axis=0)
        max_point = np.max(self.control_points, axis=0)
        
        return min_point, max_point
    
    def __repr__(self):
        return (f"IGESNURBSCurve(degree={self.degree}, "
                f"control_points={self.num_control_points()}, "
                f"knots={self.num_knots()}, "
                f"periodic={self.is_periodic}, "
                f"rational={self.is_rational})")
