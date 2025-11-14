"""IGES数据类的基类"""
import numpy as np
from abc import ABC, abstractmethod
from typing import Any


class IGESEntity(ABC):
    """IGES实体的基类"""
    
    def __init__(self):
        self.entity_type: int = 0  # IGES实体类型编号
        self.form_number: int = 0  # IGES表单编号
        self.raw_params: Any = None  # 原始参数数据
    
    @abstractmethod
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析数据
        
        Args:
            entity: IGES实体对象
            reader: IGESControl_Reader对象
        """
        pass
    
    def _set_basic_info(self, entity):
        """设置基本信息"""
        self.entity_type = entity.TypeNumber()
        self.form_number = entity.FormNumber()
        try:
            self.raw_params = entity.ParameterData()
        except:
            self.raw_params = None
    
    @staticmethod
    def coord_to_array(coord) -> np.ndarray:
        """将OCC坐标转换为numpy数组
        
        Args:
            coord: gp_Pnt或Coord()返回的元组
            
        Returns:
            numpy数组 [x, y, z]
        """
        if hasattr(coord, 'X'):
            # gp_Pnt对象
            return np.array([coord.X(), coord.Y(), coord.Z()], dtype=np.float64)
        else:
            # 元组
            return np.array(list(coord), dtype=np.float64)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.entity_type}, form={self.form_number})"
