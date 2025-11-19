import os
from typing import List, Dict, Any, Optional

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
from jcd_manage.Method.path import removeFile
from jcd_manage.Method.io import read_by_surface_type


def convertJCDFile(
    jcd_file_path: str,
    save_txt_file_path: Optional[str] = None,
    overwrite: bool = False,
    return_data: bool = True,
) -> List[Dict[str, Any]]:
    """转换JCD文件
    
    Args:
        jcd_file_path: JCD文件路径
        save_txt_file_path: 保存的文本文件路径（可选）
        overwrite: 是否覆盖已存在的文件
        return_data: 是否返回数据（默认True）
        
    Returns:
        包含所有实体数据的列表，每个元素是一个字典
    """
    # 如果需要保存文本文件
    if save_txt_file_path:
        if os.path.exists(save_txt_file_path):
            if not overwrite:
                print(f"文件已存在，跳过: {save_txt_file_path}")
                if return_data:
                    # 如果需要返回数据，仍然需要读取文件
                    pass
                else:
                    return []
            else:
                removeFile(save_txt_file_path)

    if not os.path.exists(jcd_file_path):
        print('[ERROR][::convertJCDFile]')
        print('\t jcd file not exist!')
        print('\t jcd_file_path:', jcd_file_path)
        return []

    # 存储所有实体数据
    all_entities = []
    
    with open(jcd_file_path, 'rb') as jcd_file:
        # 读取并验证文件头
        jcd_header_str = JCD_HEADER
        header = jcd_file.read(len(jcd_header_str)).decode('utf-8')

        if header != jcd_header_str:
            print(f'Header error, expected: {jcd_header_str}, got: {header}')
            return []

        entity_index = 0
        
        while True:
            # 读取标志位
            end_flag = jcd_file.read(1)
            
            if not end_flag:
                break
                
            flag_char = chr(end_flag[-1])
            
            if flag_char == ':':
                # 读取下一个物体
                print(f"\n{'='*60}")
                print(f"读取实体 #{entity_index}")
                print(f"{'='*60}")
            elif flag_char == '#':
                # 文件结束标志
                print(f"\n{'='*60}")
                print("文件读取完成")
                print(f"{'='*60}")
                break
            elif flag_char == '%':
                # 前一个bool曲面的结束标志
                print("Bool曲面结束标志")
                continue
            else:
                print(f"未知标志位: {end_flag.hex()}")
                break

            # 读取元信息
            meta_info = jcd_file.read(8)
            surface_type = SurfaceType(int.from_bytes(meta_info[0:1], 'little'))
            
            print(f"曲面类型: {surface_type}")
            print(f"元信息: {meta_info.hex()}")
            
            # 读取曲面数据
            entity_data = read_by_surface_type(jcd_file, surface_type)
            
            # 添加元信息
            entity_data['entity_index'] = entity_index
            entity_data['meta_info'] = meta_info
            
            # 保存到列表
            all_entities.append(entity_data)
            
            # 打印摘要
            print_entity_summary(entity_data)
            
            entity_index += 1

    # 打印总体统计
    print(f"\n{'='*60}")
    print(f"总共读取 {len(all_entities)} 个实体")
    print_overall_summary(all_entities)
    print(f"{'='*60}\n")
    
    # 如果需要保存文本文件
    if save_txt_file_path:
        save_entities_to_text(all_entities, save_txt_file_path)
        print(f"数据已保存到: {save_txt_file_path}")
    
    return all_entities


def print_entity_summary(entity_data: Dict[str, Any]):
    """打印单个实体的摘要信息"""
    surface_type = entity_data.get('surface_type')
    
    print(f"\n实体摘要:")
    print(f"  类型: {surface_type}")
    
    if 'matrices' in entity_data and len(entity_data['matrices']) > 0:
        print(f"  矩阵数量: {len(entity_data['matrices'])}")
    
    if 'material_name' in entity_data:
        print(f"  材质: {entity_data['material_name']}")
    
    if 'points' in entity_data and len(entity_data['points']) > 0:
        print(f"  点数量: {len(entity_data['points'])}")
        print(f"  点形状: {entity_data['points'].shape}")
    
    if 'ring_count' in entity_data:
        print(f"  环数量: {entity_data['ring_count']}")
        print(f"  原始点数: {entity_data['original_point_count']}")
    
    if 'curve_type' in entity_data:
        print(f"  曲线类型: {entity_data['curve_type']}")
    
    if 'diamond_type' in entity_data:
        print(f"  钻石类型: {entity_data['diamond_type']}")
    
    if 'bool_type' in entity_data:
        print(f"  布尔类型: {entity_data['bool_type']}")
        if 'sub_surface' in entity_data:
            print(f"  子曲面类型: {entity_data['sub_surface'].get('surface_type')}")


def print_overall_summary(all_entities: List[Dict[str, Any]]):
    """打印总体统计信息"""
    from collections import Counter
    
    # 统计类型分布
    type_counter = Counter(e['surface_type'] for e in all_entities)
    
    print("\n类型分布:")
    for surface_type, count in type_counter.items():
        print(f"  {surface_type}: {count}")
    
    # 统计总点数
    total_points = sum(
        len(e.get('points', [])) 
        for e in all_entities 
        if 'points' in e
    )
    print(f"\n总控制点数: {total_points}")
    
    # 统计材质
    materials = set(
        e.get('material_name') 
        for e in all_entities 
        if 'material_name' in e and e.get('material_name')
    )
    if materials:
        print(f"材质种类: {len(materials)}")
        for material in sorted(materials):
            print(f"  - {material}")


def save_entities_to_text(all_entities: List[Dict[str, Any]], file_path: str):
    """将实体数据保存到文本文件"""
    import numpy as np
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("JCD文件解析结果\n")
        f.write("="*80 + "\n\n")
        
        for i, entity in enumerate(all_entities):
            f.write(f"实体 #{i}\n")
            f.write("-"*80 + "\n")
            f.write(f"类型: {entity.get('surface_type')}\n")
            
            if 'material_name' in entity:
                f.write(f"材质: {entity['material_name']}\n")
            
            if 'matrices' in entity and len(entity['matrices']) > 0:
                f.write(f"\n矩阵 (数量: {len(entity['matrices'])}):\n")
                for j, matrix in enumerate(entity['matrices']):
                    f.write(f"  矩阵 {j}:\n")
                    f.write(f"{matrix}\n")
            
            if 'points' in entity and len(entity['points']) > 0:
                f.write(f"\n点 (数量: {len(entity['points'])}, 形状: {entity['points'].shape}):\n")
                # 只打印前10个点
                points_to_show = min(10, len(entity['points']))
                for j in range(points_to_show):
                    f.write(f"  {entity['points'][j]}\n")
                if len(entity['points']) > 10:
                    f.write(f"  ... (还有 {len(entity['points']) - 10} 个点)\n")
            
            if 'ring_count' in entity:
                f.write(f"\n环数量: {entity['ring_count']}\n")
                f.write(f"原始点数: {entity['original_point_count']}\n")
            
            f.write("\n" + "="*80 + "\n\n")
