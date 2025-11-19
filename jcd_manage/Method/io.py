import struct

from jcd_manage.Config.types import SurfaceType, DiamondType, BlockType, BoolType, CurveType


def read_matrix(jcd_file, matrix_count):
    for i in range(matrix_count):
        print(f"matrix {i}:")
        matrix = ''
        for j in range(4):
            matrix += '['
            for k in range(4):
                value = struct.unpack('<f', jcd_file.read(4))[0]
                matrix += f'{value:.2f}, '
            matrix += ']\n'
        print(matrix)
        #两个矩阵之间间隔4个字节
        if i != matrix_count - 1:
            unkown_data = jcd_file.read(4)
            print(f"unkown_data: {unkown_data.hex()} {unkown_data}")

def read_points(jcd_file):
    point_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"point_size: {point_size}")

    #点
    for i in range(point_size):
        point = struct.unpack('<ffff', jcd_file.read(16))
        print(f"x: {point[0]:.2f}, y: {point[1]:.2f}, z: {point[2]:.2f}, w: {point[3]:.2f}")

def read_int_points(jcd_file):
    point_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"int point_size: {point_size}")

    #点
    for i in range(point_size):
        point = struct.unpack('<iiii', jcd_file.read(16))
        print(f"int point: {point}")

def read_material(jcd_file):
    #材质名长度
    material_name_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"material_name_size: {material_name_size}")

    #材质名
    material_name = jcd_file.read(material_name_size).decode('utf-8')
    print(f"material_name: {material_name}")

#读取曲线点的数量和曲线数量，曲面的总控制点数量 = ring_count * original_point_count
def read_ring_count(jcd_file):
    ring_count = int.from_bytes(jcd_file.read(4), 'little')
    original_point_count = int.from_bytes(jcd_file.read(4), 'little')
    print(f"curve count: {ring_count}, curve point count: {original_point_count}")

def read_curve_type(jcd_file):
    curve_type = CurveType(int.from_bytes(jcd_file.read(1), 'little'))
    print(f"curve_type: {curve_type}")

#读取每个物体的矩阵
def read_matrix_by_type(jcd_file, type: SurfaceType):
    if type == SurfaceType.CURVE:
        read_matrix(jcd_file, 2)
    elif type == SurfaceType.SURFACE:
        read_matrix(jcd_file, 2)
    elif type == SurfaceType.FONT_SURFACE:
        read_matrix(jcd_file, 2)
    elif type == SurfaceType.BOOL_SURFACE:
        read_matrix(jcd_file, 3)
    elif type == SurfaceType.DIAMOND:
        read_matrix(jcd_file, 2)
    elif type == SurfaceType.GUIDE_LINE:
        read_matrix(jcd_file, 1)
    elif type == SurfaceType.QUAD_TYPE:
        read_matrix(jcd_file, 2)

#曲线
def read_curve(jcd_file):
    read_material(jcd_file)
    read_points(jcd_file)
    read_ring_count(jcd_file)
    read_curve_type(jcd_file)

    unkown_data = jcd_file.read(9)
    print(f"unkown_data: {unkown_data.hex()}")

#曲面
def read_surface(jcd_file):
    read_material(jcd_file)
    read_points(jcd_file)
    read_ring_count(jcd_file)
    read_curve_type(jcd_file)

    unkown_data = jcd_file.read(49)
    print(f"unkown_data: {unkown_data.hex()}")

#钻石
def read_diamond(jcd_file):
    read_material(jcd_file)
    read_matrix(jcd_file, 1)
    diamond_type = int.from_bytes(jcd_file.read(1), 'little')
    print(f"diamond_type: {DiamondType(diamond_type)}")
    unkown_data = jcd_file.read(3)
    print(f"unkown_data: {unkown_data.hex()}")

#字体面片
def read_font_surface(jcd_file):
    read_material(jcd_file)
    read_matrix(jcd_file, 1)
    outline_count = int.from_bytes(jcd_file.read(4), 'little') #轮廓数量
    type2 = int.from_bytes(jcd_file.read(4), 'little')
    type3 = int.from_bytes(jcd_file.read(4), 'little')
    type4 = int.from_bytes(jcd_file.read(4), 'little')
    foreground_type = BlockType(int.from_bytes(jcd_file.read(4), 'little'))
    background_type = BlockType(int.from_bytes(jcd_file.read(4), 'little'))
    thickness = struct.unpack('<f', jcd_file.read(4))[0]
    radius = struct.unpack('<f', jcd_file.read(4))[0]
    print(f"outline_count: {outline_count}, type2: {type2}, type3: {type3}, type4: {type4}, foreground_type: {foreground_type}, background_type: {background_type}, thickness: {thickness}, radius: {radius}")

    #轮廓点
    point_size = 0
    for i in range(outline_count):
        size = int.from_bytes(jcd_file.read(4), 'little')
        unkown_data = jcd_file.read(4)
        print(f"outline {i} size: {size}, unkown_data: {unkown_data.hex()}")
        point_size += size

    for i in range(point_size):
        point = struct.unpack('<fff', jcd_file.read(12))
        print(f"x: {point[0]:.2f}, y: {point[1]:.2f}, z: {point[2]:.2f}")

#辅助线
def read_guide_line(jcd_file):
    read_matrix(jcd_file, 1)
    unkown_data1 = jcd_file.read(4)
    unkwon_data2 = int.from_bytes(jcd_file.read(4), 'little')
    unkown_data3 = int.from_bytes(jcd_file.read(4), 'little')
    print(f"unkown_data1: {unkown_data1.hex()}, unkwon_data2: {unkwon_data2}, unkown_data3: {unkown_data3}")

#布尔曲面
def read_bool_surface(jcd_file):
    bool_type = BoolType(int.from_bytes(jcd_file.read(1), 'little')) #bool类型
    unkown_data = jcd_file.read(2)
    print(f"bool_type: {bool_type}")
    print(f"unkown_data: {unkown_data.hex()}")
    surface_type = SurfaceType(int.from_bytes(jcd_file.read(1), 'little')) #32代表bool 曲面，3代表普通曲面
    unkown_data = jcd_file.read(7)
    print(f"unkown_data: {unkown_data.hex()}")
    print(f"surface_type: {surface_type}")
    read_by_surface_type(jcd_file, surface_type)

#四边形面片
def read_quad_type(jcd_file):
    read_material(jcd_file)
    read_points(jcd_file)
    read_int_points(jcd_file) #顶点索引

def read_by_surface_type(jcd_file, surface_type: SurfaceType):
    read_matrix_by_type(jcd_file, surface_type)
    if surface_type == SurfaceType.CURVE:
        read_curve(jcd_file)
    elif surface_type == SurfaceType.SURFACE:
        read_surface(jcd_file)
    elif surface_type == SurfaceType.BOOL_SURFACE:
        read_bool_surface(jcd_file)
    elif surface_type == SurfaceType.DIAMOND:
        read_diamond(jcd_file)
    elif surface_type == SurfaceType.FONT_SURFACE:
        read_font_surface(jcd_file)
    elif surface_type == SurfaceType.GUIDE_LINE:
        read_guide_line(jcd_file)
    elif surface_type == SurfaceType.QUAD_TYPE:
        read_quad_type(jcd_file)
