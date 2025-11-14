"""IGES文件加载器 - 面向对象版本"""
import sys
from typing import List, Optional
from pathlib import Path

from jcd_manage.Data import (
    IGESEntity,
    IGESLine,
    IGESCircularArc,
    IGESSplineCurve,
    IGESNURBSCurve,
    IGESNURBSSurface,
    IGESTrimmedSurface,
    IGESBoundedSurface,
    IGESGenericEntity,
)


class IGESLoader:
    """IGES文件加载器
    
    使用面向对象的方式加载和解析IGES文件
    """
    
    # IGES实体类型映射
    ENTITY_TYPE_MAP = {
        100: IGESCircularArc,      # 圆弧
        110: IGESLine,              # 直线
        112: IGESSplineCurve,       # 参数样条曲线
        126: IGESNURBSCurve,        # NURBS曲线
        128: IGESNURBSSurface,      # NURBS曲面
        143: IGESBoundedSurface,    # 有界曲面
        144: IGESTrimmedSurface,    # 裁剪曲面
    }
    
    def __init__(self, file_path: str):
        """初始化加载器
        
        Args:
            file_path: IGES文件路径
        """
        self.file_path = Path(file_path)
        self.entities: List[IGESEntity] = []
        self.reader = None
        self.model = None
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"IGES file not found: {file_path}")
    
    def load(self) -> List[IGESEntity]:
        """加载IGES文件
        
        Returns:
            实体列表
        """
        try:
            from OCC.Core.IGESControl import IGESControl_Reader
        except ImportError:
            raise ImportError(
                "pythonocc-core is required to load IGES files. "
                "Install it with: conda install -c conda-forge pythonocc-core"
            )
        
        # 创建读取器
        self.reader = IGESControl_Reader()
        
        # 读取文件
        status = self.reader.ReadFile(str(self.file_path))
        
        if status != 1:
            raise RuntimeError(f"Failed to load IGES file: {self.file_path}")
        
        # 转换根实体
        self.reader.TransferRoots()
        
        # 获取模型 - 修复：使用正确的API
        self.model = self.reader.WS().Model()
        num_entities = self.model.NbEntities()
        
        print(f"\n✔ Loaded IGES: {self.file_path.name}")
        print(f"✔ Total Entities: {num_entities}")
        
        # 解析所有实体 - 修复：使用Value()而不是Entity()
        print(f"\n开始解析实体...")
        for i in range(1, num_entities + 1):
            try:
                # 正确的方法是使用Value()
                entity = self.model.Value(i)
                parsed_entity = self._parse_entity(entity)
                
                if parsed_entity:
                    self.entities.append(parsed_entity)
                    print(f"  ✓ 实体 {i}: {type(parsed_entity).__name__}")
                else:
                    print(f"  ✗ 实体 {i}: 解析返回None")
            except Exception as e:
                print(f"  ✗ 实体 {i}: 异常 - {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n解析完成，共解析 {len(self.entities)}/{num_entities} 个实体")
        return self.entities
    
    def _parse_entity(self, entity) -> Optional[IGESEntity]:
        """解析单个IGES实体
        
        Args:
            entity: IGES实体对象
            
        Returns:
            解析后的实体对象，如果无法解析则返回None
        """
        try:
            # 需要将Standard_Transient转换为IGESData_IGESEntity
            from OCC.Core.IGESData import IGESData_IGESEntity
            
            # 使用DownCast转换为IGESData_IGESEntity
            iges_entity = IGESData_IGESEntity.DownCast(entity)
            
            if not iges_entity:
                print(f"      无法转换为IGESData_IGESEntity")
                return None
            
            entity_type = iges_entity.TypeNumber()
            form_number = iges_entity.FormNumber()
        except Exception as e:
            # 如果实体无法获取类型，跳过
            print(f"      无法获取实体类型: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 获取对应的类
        entity_class = self.ENTITY_TYPE_MAP.get(entity_type, IGESGenericEntity)
        
        # 创建实例
        parsed_entity = entity_class()
        
        # 从IGES实体解析数据
        try:
            parsed_entity.from_iges_entity(iges_entity, self.reader)
            return parsed_entity
        except Exception as e:
            print(f"      解析失败 (type={entity_type}, form={form_number}): {e}")
            import traceback
            traceback.print_exc()
            
            # 创建通用实体作为后备
            try:
                generic_entity = IGESGenericEntity()
                generic_entity.from_iges_entity(iges_entity, self.reader)
                return generic_entity
            except Exception as e2:
                print(f"      通用实体也失败: {e2}")
                return None
    
    def get_entities_by_type(self, entity_class) -> List[IGESEntity]:
        """根据类型获取实体
        
        Args:
            entity_class: 实体类
            
        Returns:
            指定类型的实体列表
        """
        return [e for e in self.entities if isinstance(e, entity_class)]
    
    def get_curves(self) -> List[IGESEntity]:
        """获取所有曲线实体
        
        Returns:
            曲线实体列表
        """
        curve_types = (IGESLine, IGESCircularArc, IGESSplineCurve, IGESNURBSCurve)
        return [e for e in self.entities if isinstance(e, curve_types)]
    
    def get_surfaces(self) -> List[IGESEntity]:
        """获取所有曲面实体
        
        Returns:
            曲面实体列表
        """
        surface_types = (IGESNURBSSurface, IGESTrimmedSurface, IGESBoundedSurface)
        return [e for e in self.entities if isinstance(e, surface_types)]
    
    def print_summary(self):
        """打印文件摘要"""
        from collections import Counter
        
        print("\n" + "="*60)
        print("IGES文件摘要")
        print("="*60)
        print(f"文件: {self.file_path.name}")
        print(f"实体总数: {len(self.entities)}")
        
        # 统计实体类型
        type_counts = Counter(type(e).__name__ for e in self.entities)
        
        print("\n实体类型分布:")
        for entity_type, count in sorted(type_counts.items()):
            print(f"  {entity_type}: {count}")
        
        # 曲线统计
        curves = self.get_curves()
        if curves:
            print(f"\n曲线总数: {len(curves)}")
            curve_type_counts = Counter(type(c).__name__ for c in curves)
            for curve_type, count in sorted(curve_type_counts.items()):
                print(f"  {curve_type}: {count}")
        
        # 曲面统计
        surfaces = self.get_surfaces()
        if surfaces:
            print(f"\n曲面总数: {len(surfaces)}")
            surface_type_counts = Counter(type(s).__name__ for s in surfaces)
            for surface_type, count in sorted(surface_type_counts.items()):
                print(f"  {surface_type}: {count}")
    
    def print_details(self, max_entities: int = 10):
        """打印详细信息
        
        Args:
            max_entities: 最多打印的实体数量
        """
        print("\n" + "="*60)
        print("实体详细信息")
        print("="*60)
        
        for i, entity in enumerate(self.entities[:max_entities]):
            print(f"\n实体 #{i+1}")
            print(f"  {entity}")
            
            # 打印特定类型的额外信息
            if isinstance(entity, IGESNURBSCurve):
                min_pt, max_pt = entity.bounding_box()
                print(f"  边界框: {min_pt} ~ {max_pt}")
                print(f"  闭合: {entity.is_closed()}")
            
            elif isinstance(entity, IGESNURBSSurface):
                min_pt, max_pt = entity.bounding_box()
                print(f"  边界框: {min_pt} ~ {max_pt}")
        
        if len(self.entities) > max_entities:
            print(f"\n... 还有 {len(self.entities) - max_entities} 个实体未显示")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python iges_loader.py <iges_file>")
        print("\n示例:")
        print("  python iges_loader.py model.igs")
        print("  python iges_loader.py model.iges")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # 创建加载器并加载文件
        loader = IGESLoader(file_path)
        entities = loader.load()
        
        # 打印摘要
        loader.print_summary()
        
        # 打印详细信息
        loader.print_details(max_entities=5)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
