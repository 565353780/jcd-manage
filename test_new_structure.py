#!/usr/bin/env python3
"""
测试新的数据结构 - 验证所有类都能正确导入和初始化
"""
import numpy as np
from io import BytesIO
import struct


def test_imports():
    """测试所有类是否能正确导入"""
    print("测试导入...")
    try:
        from jcd_manage.Data import (
            BaseData, Curve, Surface, Diamond, FontSurface,
            GuideLine, BoolSurface, QuadType
        )
        print("✓ 所有类导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_base_data_methods():
    """测试BaseData的基础方法"""
    print("\n测试BaseData方法...")
    from jcd_manage.Data.base import BaseData
    
    try:
        # 创建测试数据流
        # 测试read_int
        data = BytesIO(struct.pack('<i', 42))
        assert BaseData.read_int(data) == 42
        print("✓ read_int 正常")
        
        # 测试read_float
        data = BytesIO(struct.pack('<f', 3.14))
        result = BaseData.read_float(data)
        assert abs(result - 3.14) < 0.01
        print("✓ read_float 正常")
        
        # 测试read_byte
        data = BytesIO(b'\x05')
        assert BaseData.read_byte(data) == 5
        print("✓ read_byte 正常")
        
        # 测试read_string
        test_str = "测试字符串"
        str_bytes = test_str.encode('utf-8')
        data = BytesIO(struct.pack('<i', len(str_bytes)) + str_bytes)
        assert BaseData.read_string(data) == test_str
        print("✓ read_string 正常")
        
        # 测试read_matrix
        matrix_data = struct.pack('<16f', *range(16))
        data = BytesIO(matrix_data)
        matrix = BaseData.read_matrix(data)
        assert matrix.shape == (4, 4)
        assert isinstance(matrix, np.ndarray)
        print("✓ read_matrix 正常")
        
        # 测试read_points
        point_count = 3
        points_data = struct.pack('<i', point_count)  # 点数量
        points_data += struct.pack('<12f', 1.0, 2.0, 3.0, 1.0,
                                           4.0, 5.0, 6.0, 1.0,
                                           7.0, 8.0, 9.0, 1.0)
        data = BytesIO(points_data)
        points = BaseData.read_points(data)
        assert points.shape == (3, 4)
        assert isinstance(points, np.ndarray)
        print("✓ read_points 正常")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_class_instantiation():
    """测试所有类能否正确实例化"""
    print("\n测试类实例化...")
    from jcd_manage.Data import (
        Curve, Surface, Diamond, FontSurface,
        GuideLine, BoolSurface, QuadType
    )
    
    classes = [
        ('Curve', Curve),
        ('Surface', Surface),
        ('Diamond', Diamond),
        ('FontSurface', FontSurface),
        ('GuideLine', GuideLine),
        ('BoolSurface', BoolSurface),
        ('QuadType', QuadType),
    ]
    
    all_ok = True
    for name, cls in classes:
        try:
            obj = cls()
            print(f"✓ {name} 实例化成功")
        except Exception as e:
            print(f"✗ {name} 实例化失败: {e}")
            all_ok = False
    
    return all_ok


def test_numpy_arrays():
    """测试numpy数组的基本操作"""
    print("\n测试numpy数组操作...")
    from jcd_manage.Data import Curve
    
    try:
        curve = Curve()
        
        # 模拟设置点数据
        curve.points = np.array([
            [1.0, 2.0, 3.0, 1.0],
            [4.0, 5.0, 6.0, 1.0],
            [7.0, 8.0, 9.0, 1.0],
        ], dtype=np.float32)
        
        # 测试numpy操作
        assert curve.points.shape == (3, 4)
        
        # 获取xyz坐标
        xyz = curve.points[:, :3]
        assert xyz.shape == (3, 3)
        
        # 计算边界框
        min_point = np.min(xyz, axis=0)
        max_point = np.max(xyz, axis=0)
        assert len(min_point) == 3
        assert len(max_point) == 3
        
        print("✓ numpy数组操作正常")
        return True
    except Exception as e:
        print(f"✗ numpy数组操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("="*60)
    print("JCD Manage 新架构测试")
    print("="*60)
    
    tests = [
        test_imports,
        test_base_data_methods,
        test_class_instantiation,
        test_numpy_arrays,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
