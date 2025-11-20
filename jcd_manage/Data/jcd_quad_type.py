"""JCD四边形面片数据类"""
import numpy as np
from typing import Dict, Any, Optional
from jcd_manage.Data.jcd_base import JCDBaseData


class JCDQuadType(JCDBaseData):
    """JCD四边形面片类
    
    存储四边形面片数据，包括顶点和索引
    """
    
    def __init__(self):
        super().__init__()
        self.material_name: str = ""
        self.points: np.ndarray = np.array([]).reshape(0, 4)  # 顶点 (n, 4)
        self.indices: np.ndarray = np.array([]).reshape(0, 4)  # 顶点索引 (m, 4)
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """从字典加载四边形面片数据"""
        super()._load_from_dict(data)
        self.material_name = data.get('material_name', '')
        self.points = data.get('points', np.array([]).reshape(0, 4))
        self.indices = data.get('indices', np.array([]).reshape(0, 4))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'material_name': self.material_name,
            'points': self.points,
            'indices': self.indices,
        })
        return data
    
    def get_bounding_box(self) -> Optional[tuple]:
        """计算顶点的边界框"""
        if len(self.points) == 0:
            return None
        
        min_point = np.min(self.points[:, :3], axis=0)
        max_point = np.max(self.points[:, :3], axis=0)
        return min_point, max_point
    
    def get_quad(self, index: int) -> Optional[np.ndarray]:
        """获取指定索引的四边形顶点
        
        Args:
            index: 四边形索引
            
        Returns:
            4个顶点的数组 (4, 4) 或None
        """
        if index < 0 or index >= len(self.indices):
            return None
        
        quad_indices = self.indices[index]
        
        # 检查索引是否有效
        if np.any(quad_indices < 0) or np.any(quad_indices >= len(self.points)):
            return None
        
        return self.points[quad_indices]
    
    def get_all_quads(self) -> list:
        """获取所有四边形
        
        Returns:
            四边形顶点列表
        """
        quads = []
        for i in range(len(self.indices)):
            quad = self.get_quad(i)
            if quad is not None:
                quads.append(quad)
        return quads
    
    def num_vertices(self) -> int:
        """返回顶点数量"""
        return len(self.points)
    
    def num_quads(self) -> int:
        """返回四边形数量"""
        return len(self.indices)
    
    def transform_points(self, matrix: np.ndarray):
        """变换所有顶点
        
        Args:
            matrix: 4x4变换矩阵
        """
        if len(self.points) == 0:
            return
        
        # 应用齐次坐标变换
        transformed = (matrix @ self.points.T).T
        self.points = transformed
    
    def compute_normals(self) -> np.ndarray:
        """计算每个四边形的法向量
        
        Returns:
            法向量数组 (num_quads, 3)
        """
        num_quads = self.num_quads()
        normals = np.zeros((num_quads, 3), dtype=np.float32)
        
        for i in range(num_quads):
            quad = self.get_quad(i)
            if quad is not None:
                # 使用前三个顶点计算法向量
                v1 = quad[1, :3] - quad[0, :3]
                v2 = quad[2, :3] - quad[0, :3]
                normal = np.cross(v1, v2)
                
                # 归一化
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normals[i] = normal / norm
        
        return normals
    
    def get_points(self) -> Optional[np.ndarray]:
        """获取原始点数据
        
        Returns:
            点数组 (n, 3)
        """
        if len(self.points) == 0:
            return None
        return self.points[:, :3]
    
    def __repr__(self):
        return (f"JCDQuadType(material='{self.material_name}', "
                f"vertices={self.num_vertices()}, "
                f"quads={self.num_quads()}, "
                f"hide={self.hide})")
