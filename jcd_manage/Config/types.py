from enum import Enum, auto


class SurfaceType(Enum):
    CURVE = 2 #曲线
    SURFACE = 3 #曲面
    FONT_SURFACE = 5 #字体
    BOOL_SURFACE = 32 #布尔曲面
    DIAMOND = 99 #钻石
    GUIDE_LINE = 90 #辅助线
    QUAD_TYPE = 4 #四边形面片
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        print(f"unkown surface type: {value}")
        return cls.UNKNOWN

class DiamondType(Enum):
    ROUND = 0 # 圆形钻石
    MARQUISE = 1 # 马眼钻石
    PEAR = 2 # 梨形钻石
    HEART = 3 # 心形钻石
    OCTAGON = 4 # 八方钻石
    SQUARE = 8 # 方形钻石
    TRIANGLE = 9 # 三角钻石

class BlockType(Enum):
    ANGLE = 0 # 尖角
    ROUND = 1 # 圆角
    CUT = 2 # 切角

class BoolType(Enum):
    UNION = 2 # 并集
    INTERSECTION = 3 # 交集
    DIFFERENCE = 4 # 差集

class CurveType(Enum):
    OPEN_CURVE = 0 # 开放曲线
    CLOSED_CURVE = 1 # 闭合曲线

class DAGNodeType(Enum):
    PRIMITIVE = auto()
    GROUP = auto()
    BOOLEAN = auto()

class DAGBoolType(Enum):
    UNION = "union"
    INTERSECT = "intersect"
    DIFFERENCE = "difference"
