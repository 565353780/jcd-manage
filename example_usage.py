#!/usr/bin/env python3
"""
JCD文件读取示例 - 展示如何使用面向对象的方式读取和处理JCD文件
"""
import sys
import numpy as np
from jcd_manage.Module.jcd_reader import JCDReader
from jcd_manage.Data import Curve, Surface, Diamond


def print_object_info(obj):
    """打印对象详细信息"""
    print(f"\n{'='*60}")
    print(f"对象类型: {type(obj).__name__}")
    print(f"{'='*60}")
    
    # 打印材质信息（如果有）
    if hasattr(obj, 'material_name'):
        print(f"材质名称: {obj.material_name}")
    
    # 打印矩阵信息
    if hasattr(obj, 'matrices') and obj.matrices.size > 0:
        print(f"矩阵数量: {len(obj.matrices)}")
        for i, matrix in enumerate(obj.matrices):
            print(f"\n矩阵 {i+1}:")
            print(matrix)
    
    # 打印点信息
    if hasattr(obj, 'points') and obj.points.size > 0:
        print(f"\n点数量: {len(obj.points)}")
        print(f"点数组形状: {obj.points.shape}")
        print(f"前5个点:")
        for i, point in enumerate(obj.points[:5]):
            print(f"  {i+1}. {point}")
        if len(obj.points) > 5:
            print(f"  ... (还有 {len(obj.points) - 5} 个点)")
    
    # 曲线/曲面特有信息
    if isinstance(obj, (Curve, Surface)):
        print(f"\n曲线数量: {obj.ring_count}")
        print(f"每条曲线的点数: {obj.original_point_count}")
        print(f"曲线类型: {obj.curve_type}")
    
    # 钻石特有信息
    if isinstance(obj, Diamond):
        print(f"\n钻石类型: {obj.diamond_type}")
        if obj.matrix.size > 0:
            print(f"钻石矩阵:")
            print(obj.matrix)


def analyze_jcd_file(file_path: str):
    """分析JCD文件"""
    print(f"正在读取JCD文件: {file_path}\n")
    
    # 创建读取器并读取文件
    reader = JCDReader(file_path)
    objects = reader.read()
    
    print(f"\n{'#'*60}")
    print(f"文件统计信息")
    print(f"{'#'*60}")
    print(f"文件大小: {reader.file_size} 字节")
    print(f"对象总数: {len(objects)}")
    
    # 统计各类型对象数量
    type_counts = {}
    for obj in objects:
        obj_type = type(obj).__name__
        type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
    
    print(f"\n对象类型分布:")
    for obj_type, count in sorted(type_counts.items()):
        print(f"  {obj_type}: {count}")
    
    # 打印每个对象的详细信息
    print(f"\n{'#'*60}")
    print(f"对象详细信息")
    print(f"{'#'*60}")
    
    for i, obj in enumerate(objects):
        print(f"\n对象 #{i+1}")
        print_object_info(obj)
    
    # 数据处理示例
    print(f"\n{'#'*60}")
    print(f"数据处理示例")
    print(f"{'#'*60}")
    
    # 找出所有曲线
    curves = [obj for obj in objects if isinstance(obj, Curve)]
    if curves:
        print(f"\n找到 {len(curves)} 条曲线")
        for i, curve in enumerate(curves):
            if curve.points.size > 0:
                # 计算曲线的边界框
                min_point = np.min(curve.points[:, :3], axis=0)
                max_point = np.max(curve.points[:, :3], axis=0)
                center = (min_point + max_point) / 2
                
                print(f"\n曲线 {i+1}:")
                print(f"  材质: {curve.material_name}")
                print(f"  点数: {len(curve.points)}")
                print(f"  边界框最小点: {min_point}")
                print(f"  边界框最大点: {max_point}")
                print(f"  中心点: {center}")
    
    # 找出所有曲面
    surfaces = [obj for obj in objects if isinstance(obj, Surface)]
    if surfaces:
        print(f"\n找到 {len(surfaces)} 个曲面")
        for i, surface in enumerate(surfaces):
            print(f"\n曲面 {i+1}:")
            print(f"  材质: {surface.material_name}")
            print(f"  控制点总数: {len(surface.points)}")
            print(f"  曲线数 (U方向): {surface.ring_count}")
            print(f"  每条曲线的点数 (V方向): {surface.original_point_count}")


def main():
    if len(sys.argv) < 2:
        print("用法: python example_usage.py <jcd文件路径>")
        print("\n示例:")
        print("  python example_usage.py data/sample.jcd")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_jcd_file(file_path)


if __name__ == '__main__':
    main()
