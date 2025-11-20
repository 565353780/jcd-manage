from collections import Counter
from typing import List, Dict, Any


def print_entity_summary(entity_data: Dict[str, Any]) -> bool:
    """打印单个实体的摘要信息"""
    surface_type = entity_data.get('surface_type')
    hide = entity_data.get('hide')

    print(f"\n实体摘要:")
    print(f"  类型: {surface_type}")
    print(f"  隐藏: {hide}")

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
    return True


def print_overall_summary(all_entities: List[Dict[str, Any]]) -> bool:
    """打印总体统计信息"""
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
    return True
