"""IGES通用实体 - 用于未特别支持的实体类型"""
import numpy as np
from jcd_manage.Data.iges_base import IGESEntity


class IGESGenericEntity(IGESEntity):
    """IGES通用实体
    
    用于存储尚未特别支持的IGES实体类型
    """
    
    def __init__(self):
        super().__init__()
        self.type_name: str = "Unknown"
    
    def from_iges_entity(self, entity, reader):
        """从IGES实体解析通用数据"""
        self._set_basic_info(entity)
        
        # 根据类型设置名称
        type_names = {
            102: "Composite Curve",
            104: "Conic Arc",
            106: "Copious Data",
            108: "Plane",
            114: "Parametric Spline Surface",
            116: "Point",
            118: "Ruled Surface",
            120: "Surface of Revolution",
            122: "Tabulated Cylinder",
            124: "Transformation Matrix",
            125: "Flash",
            130: "Offset Curve",
            140: "Offset Surface",
            141: "Boundary",
            142: "Curve on a Parametric Surface",
            186: "Manifold Solid B-Rep Object",
            190: "Plane Surface",
            192: "Right Circular Cylindrical Surface",
            194: "Right Circular Conical Surface",
            196: "Spherical Surface",
            198: "Toroidal Surface",
        }
        
        self.type_name = type_names.get(self.entity_type, f"Type {self.entity_type}")
    
    def __repr__(self):
        return f"IGESGenericEntity(type={self.entity_type}, name='{self.type_name}', form={self.form_number})"
