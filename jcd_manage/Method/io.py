import struct
import numpy as np
from typing import Tuple, Dict, Any

from jcd_manage.Config.types import SurfaceType, DiamondType, BlockType, BoolType, CurveType


def read_matrix(jcd_file, matrix_count: int) -> np.ndarray:
    """读取矩阵数据

    Args:
        jcd_file: 文件对象
        matrix_count: 矩阵数量

    Returns:
        矩阵数组，形状为 (matrix_count, 4, 4)
    """
    matrices = np.zeros((matrix_count, 4, 4), dtype=np.float32)

    for i in range(matrix_count):
        for j in range(4):
            for k in range(4):
                value = struct.unpack('<f', jcd_file.read(4))[0]
                matrices[i, j, k] = value

        # 两个矩阵之间间隔4个字节
        if i != matrix_count - 1:
            unkown_data = jcd_file.read(4)

    return matrices

def read_points(jcd_file) -> np.ndarray:
    """读取浮点数点数据

    Args:
        jcd_file: 文件对象

    Returns:
        点数组，形状为 (point_size, 4)
    """
    point_size = int.from_bytes(jcd_file.read(4), 'little')

    points = np.zeros((point_size, 4), dtype=np.float32)
    for i in range(point_size):
        point = struct.unpack('<ffff', jcd_file.read(16))
        points[i] = point

    return points

def read_int_points(jcd_file) -> np.ndarray:
    """读取整数点数据（顶点索引）

    Args:
        jcd_file: 文件对象

    Returns:
        整数点数组，形状为 (point_size, 4)
    """
    point_size = int.from_bytes(jcd_file.read(4), 'little')

    points = np.zeros((point_size, 4), dtype=np.int32)
    for i in range(point_size):
        point = struct.unpack('<iiii', jcd_file.read(16))
        points[i] = point

    return points

def read_material(jcd_file) -> str:
    """读取材质名称

    Args:
        jcd_file: 文件对象

    Returns:
        材质名称字符串
    """
    material_name_size = int.from_bytes(jcd_file.read(4), 'little')
    material_name = jcd_file.read(material_name_size).decode('utf-8')
    return material_name

def read_ring_count(jcd_file) -> Tuple[int, int]:
    """读取曲线点的数量和曲线数量

    曲面的总控制点数量 = ring_count * original_point_count

    Args:
        jcd_file: 文件对象

    Returns:
        (ring_count, original_point_count) 元组
    """
    ring_count = int.from_bytes(jcd_file.read(4), 'little')
    original_point_count = int.from_bytes(jcd_file.read(4), 'little')
    return ring_count, original_point_count

def read_curve_type(jcd_file) -> CurveType:
    """读取曲线类型

    Args:
        jcd_file: 文件对象

    Returns:
        CurveType 枚举值
    """
    curve_type = CurveType(int.from_bytes(jcd_file.read(1), 'little'))
    return curve_type

def read_matrix_by_type(jcd_file, type: SurfaceType) -> np.ndarray:
    """根据类型读取对应数量的矩阵

    Args:
        jcd_file: 文件对象
        type: 曲面类型

    Returns:
        矩阵数组
    """
    matrix_count_map = {
        SurfaceType.CURVE: 2,
        SurfaceType.SURFACE: 2,
        SurfaceType.FONT_SURFACE: 2,
        SurfaceType.BOOL_SURFACE: 3,
        SurfaceType.DIAMOND: 2,
        SurfaceType.GUIDE_LINE: 1,
        SurfaceType.QUAD_TYPE: 2,
    }

    matrix_count = matrix_count_map.get(type, 0)
    if matrix_count > 0:
        return read_matrix(jcd_file, matrix_count)
    return np.array([])

def read_curve(jcd_file) -> Dict[str, Any]:
    """读取曲线数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含曲线数据的字典
    """
    material_name = read_material(jcd_file)
    points = read_points(jcd_file)
    ring_count, original_point_count = read_ring_count(jcd_file)
    curve_type = read_curve_type(jcd_file)

    unkown_data = jcd_file.read(9)

    return {
        'material_name': material_name,
        'points': points,
        'ring_count': ring_count,
        'original_point_count': original_point_count,
        'curve_type': curve_type,
        # 'unknown_data': unkown_data
    }

def read_surface(jcd_file) -> Dict[str, Any]:
    """读取曲面数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含曲面数据的字典
    """
    material_name = read_material(jcd_file)
    points = read_points(jcd_file)
    ring_count, original_point_count = read_ring_count(jcd_file)
    curve_type = read_curve_type(jcd_file)

    unkown_data = jcd_file.read(49)

    return {
        'material_name': material_name,
        'points': points,
        'ring_count': ring_count,
        'original_point_count': original_point_count,
        'curve_type': curve_type,
        # 'unknown_data': unkown_data
    }

def read_diamond(jcd_file) -> Dict[str, Any]:
    """读取钻石数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含钻石数据的字典
    """
    material_name = read_material(jcd_file)
    matrix = read_matrix(jcd_file, 1)
    diamond_type = DiamondType(int.from_bytes(jcd_file.read(1), 'little'))
    unkown_data = jcd_file.read(3)

    return {
        'material_name': material_name,
        'matrix': matrix,
        'diamond_type': diamond_type,
        # 'unknown_data': unkown_data
    }

def read_font_surface(jcd_file) -> Dict[str, Any]:
    """读取字体面片数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含字体面片数据的字典
    """
    material_name = read_material(jcd_file)
    matrix = read_matrix(jcd_file, 1)

    outline_count = int.from_bytes(jcd_file.read(4), 'little')
    type2 = int.from_bytes(jcd_file.read(4), 'little')
    type3 = int.from_bytes(jcd_file.read(4), 'little')
    type4 = int.from_bytes(jcd_file.read(4), 'little')
    foreground_type = BlockType(int.from_bytes(jcd_file.read(4), 'little'))
    background_type = BlockType(int.from_bytes(jcd_file.read(4), 'little'))
    thickness = struct.unpack('<f', jcd_file.read(4))[0]
    radius = struct.unpack('<f', jcd_file.read(4))[0]

    # 读取轮廓大小
    outline_sizes = np.zeros(outline_count, dtype=np.int32)
    point_size = 0
    for i in range(outline_count):
        size = int.from_bytes(jcd_file.read(4), 'little')
        unkown_data = jcd_file.read(4)
        outline_sizes[i] = size
        point_size += size

    # 读取所有轮廓点
    points = np.zeros((point_size, 3), dtype=np.float32)
    for i in range(point_size):
        point = struct.unpack('<fff', jcd_file.read(12))
        points[i] = point

    return {
        'material_name': material_name,
        'matrix': matrix,
        'outline_count': outline_count,
        'type2': type2,
        'type3': type3,
        'type4': type4,
        'foreground_type': foreground_type,
        'background_type': background_type,
        'thickness': thickness,
        'radius': radius,
        'outline_sizes': outline_sizes,
        'points': points
    }

def read_guide_line(jcd_file) -> Dict[str, Any]:
    """读取辅助线数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含辅助线数据的字典
    """
    matrix = read_matrix(jcd_file, 1)
    unkown_data1 = jcd_file.read(4)
    unkwon_data2 = int.from_bytes(jcd_file.read(4), 'little')
    unkown_data3 = int.from_bytes(jcd_file.read(4), 'little')

    return {
        'matrix': matrix,
        # 'unknown_data1': unkown_data1,
        # 'unknown_data2': unkwon_data2,
        # 'unknown_data3': unkown_data3
    }

def read_bool_surface(jcd_file) -> Dict[str, Any]:
    """读取布尔曲面数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含布尔曲面数据的字典
    """
    bool_type = BoolType(int.from_bytes(jcd_file.read(1), 'little'))
    unkown_data1 = jcd_file.read(2)
    surface_type = SurfaceType(int.from_bytes(jcd_file.read(1), 'little'))
    unkown_data2 = jcd_file.read(7)

    # 递归读取子曲面
    sub_surface_data = read_by_surface_type(jcd_file, surface_type)

    return {
        'bool_type': bool_type,
        # 'unknown_data1': unkown_data1,
        'surface_type': surface_type,
        # 'unknown_data2': unkown_data2,
        'sub_surface': sub_surface_data
    }

def read_quad_type(jcd_file) -> Dict[str, Any]:
    """读取四边形面片数据

    Args:
        jcd_file: 文件对象

    Returns:
        包含四边形面片数据的字典
    """
    material_name = read_material(jcd_file)
    points = read_points(jcd_file)
    indices = read_int_points(jcd_file)  # 顶点索引

    return {
        'material_name': material_name,
        'points': points,
        'indices': indices
    }


def read_by_surface_type(jcd_file, surface_type: SurfaceType) -> Dict[str, Any]:
    """根据曲面类型读取对应数据

    Args:
        jcd_file: 文件对象
        surface_type: 曲面类型

    Returns:
        包含曲面数据的字典，包括矩阵和类型特定数据
    """
    # 读取矩阵
    matrices = read_matrix_by_type(jcd_file, surface_type)

    # 根据类型读取特定数据
    type_data = {}

    if surface_type == SurfaceType.CURVE:
        type_data = read_curve(jcd_file)
    elif surface_type == SurfaceType.SURFACE:
        type_data = read_surface(jcd_file)
    elif surface_type == SurfaceType.BOOL_SURFACE:
        type_data = read_bool_surface(jcd_file)
    elif surface_type == SurfaceType.DIAMOND:
        type_data = read_diamond(jcd_file)
    elif surface_type == SurfaceType.FONT_SURFACE:
        type_data = read_font_surface(jcd_file)
    elif surface_type == SurfaceType.GUIDE_LINE:
        type_data = read_guide_line(jcd_file)
    elif surface_type == SurfaceType.QUAD_TYPE:
        type_data = read_quad_type(jcd_file)

    # 合并矩阵和类型数据
    return {
        'surface_type': surface_type,
        'matrices': matrices,
        **type_data
    }
