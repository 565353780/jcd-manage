import os
import sys
import struct

from jcd_manage.Config.types import SurfaceType, DiamondType, BlockType, BoolType, CurveType

file_name = sys.argv[1]

jcd_file = open(file_name, 'rb')
file_size = os.path.getsize(file_name)

#文件头
jcd_header_str = 'SILKIDEASIGN0100'
header = jcd_file.read(len(jcd_header_str)).decode('utf-8')

if header != jcd_header_str:
    print(f'header error header: {header}')
    exit(1)

#debug函数
def parse_4_bytes(bytes_data):
    if len(bytes_data) < 4:
        print(f"unkown data {len(bytes_data)} bytes, unkown_data: {bytes_data}")
        return

    float_value = struct.unpack('<f', bytes_data)[0]
    int_value = struct.unpack('<i', bytes_data)[0]
    short1, short2 = struct.unpack('<hh', bytes_data)
    print(f"float: {float_value}, int: {int_value}, shorts: ({short1}, {short2}), original: {bytes_data.hex()} {bytes_data}")

def read_matrix(matrix_count):
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

def read_points():
    point_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"point_size: {point_size}")

    #点
    for i in range(point_size):
        point = struct.unpack('<ffff', jcd_file.read(16))
        print(f"x: {point[0]:.2f}, y: {point[1]:.2f}, z: {point[2]:.2f}, w: {point[3]:.2f}")

def read_int_points():
    point_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"int point_size: {point_size}")

    #点
    for i in range(point_size):
        point = struct.unpack('<iiii', jcd_file.read(16))
        print(f"int point: {point}")
    
def read_material():
    #材质名长度
    material_name_size = int.from_bytes(jcd_file.read(4), 'little')
    print(f"material_name_size: {material_name_size}")

    #材质名
    material_name = jcd_file.read(material_name_size).decode('utf-8')
    print(f"material_name: {material_name}")

#读取曲线点的数量和曲线数量，曲面的总控制点数量 = ring_count * original_point_count
def read_ring_count():
    ring_count = int.from_bytes(jcd_file.read(4), 'little')
    original_point_count = int.from_bytes(jcd_file.read(4), 'little')
    print(f"curve count: {ring_count}, curve point count: {original_point_count}")

def read_curve_type():
    curve_type = CurveType(int.from_bytes(jcd_file.read(1), 'little'))
    print(f"curve_type: {curve_type}")

#读取每个物体的矩阵
def read_matrix_by_type(type: SurfaceType):
    if type == SurfaceType.CURVE:
        read_matrix(2)
    elif type == SurfaceType.SURFACE:
        read_matrix(2)
    elif type == SurfaceType.FONT_SURFACE:
        read_matrix(2)
    elif type == SurfaceType.BOOL_SURFACE:
        read_matrix(3)
    elif type == SurfaceType.DIAMOND:
        read_matrix(2)
    elif type == SurfaceType.GUIDE_LINE:
        read_matrix(1)
    elif type == SurfaceType.QUAD_TYPE:
        read_matrix(2)

#曲线
def read_curve():
    read_material()
    read_points()
    read_ring_count()
    read_curve_type()

    unkown_data = jcd_file.read(9)
    print(f"unkown_data: {unkown_data.hex()}")

#曲面
def read_surface():
    read_material()
    read_points()
    read_ring_count()
    read_curve_type()

    unkown_data = jcd_file.read(49)
    print(f"unkown_data: {unkown_data.hex()}")

#钻石
def read_diamond():
    read_material()
    read_matrix(1)
    diamond_type = int.from_bytes(jcd_file.read(1), 'little')
    print(f"diamond_type: {DiamondType(diamond_type)}")
    unkown_data = jcd_file.read(3)
    print(f"unkown_data: {unkown_data.hex()}")

#字体面片
def read_font_surface():
    read_material()
    read_matrix(1)
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
def read_guide_line():
    read_matrix(1)
    unkown_data1 = jcd_file.read(4)
    unkwon_data2 = int.from_bytes(jcd_file.read(4), 'little')
    unkown_data3 = int.from_bytes(jcd_file.read(4), 'little')
    print(f"unkown_data1: {unkown_data1.hex()}, unkwon_data2: {unkwon_data2}, unkown_data3: {unkown_data3}")

#布尔曲面
def read_bool_surface():
    bool_type = BoolType(int.from_bytes(jcd_file.read(1), 'little')) #bool类型
    unkown_data = jcd_file.read(2)
    print(f"bool_type: {bool_type}")
    print(f"unkown_data: {unkown_data.hex()}")
    surface_type = SurfaceType(int.from_bytes(jcd_file.read(1), 'little')) #32代表bool 曲面，3代表普通曲面
    unkown_data = jcd_file.read(7)
    print(f"unkown_data: {unkown_data.hex()}")
    print(f"surface_type: {surface_type}")
    read_by_surface_type(surface_type)

#四边形面片
def read_quad_type():
    read_material()
    read_points()
    read_int_points() #顶点索引

def read_by_surface_type(surface_type: SurfaceType):
    read_matrix_by_type(surface_type)
    if surface_type == SurfaceType.CURVE:
        read_curve()
    elif surface_type == SurfaceType.SURFACE:
        read_surface()
    elif surface_type == SurfaceType.BOOL_SURFACE:
        read_bool_surface()
    elif surface_type == SurfaceType.DIAMOND:
        read_diamond()
    elif surface_type == SurfaceType.FONT_SURFACE:
        read_font_surface()
    elif surface_type == SurfaceType.GUIDE_LINE:
        read_guide_line()
    elif surface_type == SurfaceType.QUAD_TYPE:
        read_quad_type()

while True:
    end_flag = jcd_file.read(1)
    if chr(end_flag[-1]) == ':':
        print("flag :, continue") #读取下一个物体
    elif chr(end_flag[-1]) == '#':
        print("flag #, end") #文件结束标志
        exit(0)
    elif chr(end_flag[-1]) == '%':
        print("bool flag %, previous bool surface end") #前一个bool曲面的结束标志
        continue
    else:
        print(f"file headerunkown data 1 bytes, unkown_data: {end_flag}")
        exit(0)

    print("=================================================================")
    meta_info = jcd_file.read(8)
    surface_type = SurfaceType(int.from_bytes(meta_info[0:1], 'little'))
    print(f"surface_type: {surface_type}")
    print(f"meta_info: {meta_info.hex()}")
    read_by_surface_type(surface_type)
    print("=================================================================\n")
