"""JCD布尔曲面数据类 - 基于DAG结构"""
import numpy as np
from typing import Dict, Any, Optional, List
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Config.types import BoolType, DAGBoolType
from jcd_manage.Data.dag import CSGDAG, PrimitiveSurface, SurfaceGroup, BooleanOp


class JCDBoolSurface(JCDBaseData):
    """JCD布尔曲面类 - 基于DAG结构
    
    使用CSGDAG实现多曲面的布尔操作，支持复杂的布尔运算树结构
    """
    
    def __init__(self):
        super().__init__()
        self.bool_type: Optional[BoolType] = None  # 布尔操作类型
        self.unknown_data1: bytes = b''
        self.dag = CSGDAG()  # DAG管理器实例
        self.root_node_id: Optional[int] = None  # 根节点ID
        self.surface_count: int = 0  # 曲面数量计数器

    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载布尔曲面数据"""
        super()._load_from_dict(data)
        self.bool_type = data.get('bool_type')
        self.unknown_data1 = data.get('unknown_data1', b'')
        self.surface_count = data.get('surface_count', 0)

        # 重建DAG结构
        if 'dag_nodes' in data:
            # 这里简化处理，实际应该重建完整的DAG结构
            # 在loader中会动态添加节点
            pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'bool_type': self.bool_type,
            'unknown_data1': self.unknown_data1,
            'surface_count': self.surface_count,
            'root_node_id': self.root_node_id,
        })
        return data
    
    def add_surface(self, surface_data: Dict[str, Any]) -> int:
        """添加一个原始曲面对象到DAG中

        Args:
            surface_data: 曲面数据字典

        Returns:
            添加的节点ID
        """
        # 创建原始曲面节点
        primitive_node = PrimitiveSurface(surface_data)
        node_id = self.dag.add(primitive_node)
        self.surface_count += 1
        
        # 如果是第一个曲面，设置为根节点
        if self.root_node_id is None:
            self.root_node_id = node_id
        
        return node_id
    
    def create_surface_group(self, node_ids: List[int]) -> int:
        """创建曲面组节点
        
        Args:
            node_ids: 要组合的节点ID列表
            
        Returns:
            创建的组节点ID
        """
        group_node = SurfaceGroup(node_ids)
        node_id = self.dag.add(group_node)
        return node_id
    
    def apply_boolean_operation(self, bool_type: DAGBoolType, left_id: int, right_id: int) -> int:
        """应用布尔操作
        
        Args:
            bool_type: 布尔操作类型
            left_id: 左侧节点ID
            right_id: 右侧节点ID
            
        Returns:
            创建的布尔操作节点ID
        """
        bool_node = BooleanOp(bool_type, left_id, right_id)
        node_id = self.dag.add(bool_node)
        # 更新根节点为新的布尔操作节点
        self.root_node_id = node_id
        return node_id
    
    def get_bool_type_name(self) -> str:
        """获取布尔操作类型名称"""
        if self.bool_type is None:
            return "Unknown"
        
        type_names = {
            BoolType.UNION: "并集",
            BoolType.INTERSECTION: "交集",
            BoolType.DIFFERENCE: "差集",
        }
        return type_names.get(self.bool_type, str(self.bool_type))
    
    def print_dag_structure(self):
        """打印DAG结构"""
        if self.root_node_id is not None:
            print(f"布尔曲面DAG结构 (根节点ID: {self.root_node_id}):")
            self.dag.print_tree(self.root_node_id)
        else:
            print("布尔曲面DAG结构为空")
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算整体边界框
        
        Returns:
            (min_point, max_point) 或 None
        """
        if self.root_node_id is None:
            return None
        
        # 简化实现，实际应该遍历所有原始曲面节点计算边界框
        # 这里只是返回默认值，后续需要完善
        return np.array([-1, -1, -1]), np.array([1, 1, 1])
    
    def get_surface_count(self) -> int:
        """获取曲面数量"""
        return self.surface_count
    
    def get_dag(self) -> CSGDAG:
        """获取DAG实例"""
        return self.dag
    
    def get_root_node_id(self) -> Optional[int]:
        """获取根节点ID"""
        return self.root_node_id
    
    def set_root_node_id(self, node_id: int):
        """设置根节点ID"""
        self.root_node_id = node_id
    
    def __repr__(self):
        return (f"JCDBoolSurface(bool_type={self.get_bool_type_name()}, "
                f"surface_count={self.surface_count}, "
                f"root_node_id={self.root_node_id}, "
                f"hide={self.hide})")
