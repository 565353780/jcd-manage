import os
from typing import List, Dict, Any, Optional

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
from jcd_manage.Method.path import removeFile
from jcd_manage.Method.io import read_by_surface_type
from jcd_manage.Method.info import print_entity_summary, print_overall_summary


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

        while True:
            # 读取标志位
            end_flag = jcd_file.read(1)

            if not end_flag:
                break

            flag_char = chr(end_flag[-1])

            if flag_char == ':':
                pass
            elif flag_char == '#':
                break
            elif flag_char == '%':
                # 前一个bool曲面的结束标志
                continue
            else:
                print(f"未知标志位: {end_flag.hex()}")
                break

            # 读取元信息
            meta_info = jcd_file.read(8)
            hide = (int.from_bytes(meta_info[4:5], 'little') & 2) == 2
            surface_type = SurfaceType(int.from_bytes(meta_info[0:1], 'little'))

            # 读取曲面数据
            entity_data = read_by_surface_type(jcd_file, surface_type)

            # 添加元信息
            entity_data['meta_info'] = meta_info
            entity_data['hide'] = hide

            # 保存到列表
            all_entities.append(entity_data)

            # 打印摘要
            print_entity_summary(entity_data)

    # 打印总体统计
    print_overall_summary(all_entities)

    # 如果需要保存文本文件
    if save_txt_file_path:
        save_entities_to_text(all_entities, save_txt_file_path)
        print(f"数据已保存到: {save_txt_file_path}")

    return all_entities

def save_entities_to_text(all_entities: List[Dict[str, Any]], file_path: str):
    """将实体数据保存到文本文件"""
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
