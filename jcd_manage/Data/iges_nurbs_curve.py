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
        
        # 使用reader转换NURBS曲线
        curve = reader.TransferCurve(entity)
        
        # 检查是否为BSpline曲线
        from OCC.Core.Geom import Geom_BSplineCurve
        if isinstance(curve, Geom_BSplineCurve):
            self._parse_bspline_curve(curve)
        # 如果不是BSpline曲线，保留基本信息即可
    
    def _parse_bspline_curve(self, curve):
        """解析BSpline曲线对象"""
        from OCC.Core.Geom import Geom_BSplineCurve
        
        # 基本参数
        self.degree = curve.Degree()
        self.is_periodic = curve.IsPeriodic()
        self.is_rational = curve.IsRational()
        
        # 控制点
        num_poles = curve.NbPoles()
        poles = np.zeros((num_poles, 3), dtype=np.float64)
        weights = np.zeros(num_poles, dtype=np.float64)
        
        for i in range(num_poles):
            pole = curve.Pole(i + 1)  # OCC索引从1开始
            poles[i] = self.coord_to_array(pole)
            
            if self.is_rational:
                weights[i] = curve.Weight(i + 1)
            else:
                weights[i] = 1.0
        
        self.control_points = poles
        self.weights = weights
        
        # 节点向量
        num_knots = curve.NbKnots()
        knots = np.zeros(num_knots, dtype=np.float64)
        mults = np.zeros(num_knots, dtype=np.int32)
        
        for i in range(num_knots):
            knots[i] = curve.Knot(i + 1)
            mults[i] = curve.Multiplicity(i + 1)
        
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
