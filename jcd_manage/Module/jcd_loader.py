import os
from typing import Union, List, Optional

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType, BoolType, DAGBoolType
from jcd_manage.Data import (
    JCDCurve, JCDSurface, JCDDiamond, JCDFontSurface, 
    JCDGuideLine, JCDBoolSurface, JCDQuadType, JCDBaseData
)
from jcd_manage.Method.io import read_by_surface_type, save_entities_to_text
from jcd_manage.Method.info import print_entity_summary, print_overall_summary
from jcd_manage.Method.path import createFileFolder, removeFile
from jcd_manage.Method.render import renderMultipleGroups



class JCDLoader(object):
    """JCD文件加载器

    加载JCD文件并将数据转换为面向对象的数据类实例
    """

    # 类型映射
    TYPE_CLASS_MAP = {
        SurfaceType.CURVE: JCDCurve,
        SurfaceType.SURFACE: JCDSurface,
        SurfaceType.DIAMOND: JCDDiamond,
        SurfaceType.FONT_SURFACE: JCDFontSurface,
        SurfaceType.GUIDE_LINE: JCDGuideLine,
        SurfaceType.BOOL_SURFACE: JCDBoolSurface,
        SurfaceType.QUAD_TYPE: JCDQuadType,
    }

    def __init__(
        self,
        jcd_file_path: Union[str, None]=None,
        output_info: bool = False,
    ) -> None:
        self.objects: List[JCDBaseData] = []  # 现在存储数据类实例

        if jcd_file_path is not None:
            self.loadJCDFile(jcd_file_path, output_info)
        return

    def loadJCDFile(
        self,
        jcd_file_path: str,
        output_info: bool = False,
    ) -> bool:
        if not os.path.exists(jcd_file_path):
            print('[ERROR][JCDLoader::loadTXTFile]')
            print('\t jcd file not exist!')
            print('\t jcd_file_path:', jcd_file_path)
            return False

        # 存储所有实体数据
        self.objects = []
        # 当前正在构建的布尔曲面
        current_bool_surface: Optional[JCDBoolSurface] = None
        bool_operation_stack : List[(BoolType, List[int])] = []

        with open(jcd_file_path, 'rb') as jcd_file:
            # 读取并验证文件头
            jcd_header_str = JCD_HEADER
            header = jcd_file.read(len(jcd_header_str)).decode('utf-8')

            if header != jcd_header_str:
                print(f'Header error, expected: {jcd_header_str}, got: {header}')
                return False

            while True:
                # 读取标志位
                end_flag = jcd_file.read(1)

                if not end_flag:
                    break

                flag_char = chr(end_flag[-1])

                if flag_char == ':':
                    # 正常的曲面开始标志
                    pass
                elif flag_char == '#':
                    # 文件结束标志
                    break
                elif flag_char == '%':
                    # 开始构建bool曲面节点
                    bool_type_mapping = {
                        BoolType.UNION: DAGBoolType.UNION,
                        BoolType.INTERSECTION: DAGBoolType.INTERSECT,
                        BoolType.DIFFERENCE: DAGBoolType.DIFFERENCE
                    }
                    bool_operation_element = bool_operation_stack.pop() #弹出栈顶元素，标记上一个bool操作结束
                    root_node_id = None
                    for node_id in bool_operation_element[1]:
                        if root_node_id is None:
                            root_node_id = node_id
                        else:
                            bool_node_id = current_bool_surface.apply_boolean_operation(bool_type_mapping.get(bool_operation_element[0], DAGBoolType.UNION), root_node_id, node_id)
                            root_node_id = bool_node_id

                    if len(bool_operation_stack) == 0:
                        # 所有bool操作结束，添加到对象列表
                        self.objects.append(current_bool_surface)
                        current_bool_surface = None
                    else:
                        # 将root节点添加到栈顶元素的子节点列表中
                        bool_operation_stack[-1][1].append(root_node_id)
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

                # 处理布尔曲面的特殊逻辑
                if surface_type == SurfaceType.BOOL_SURFACE:
                    # 创建一个新的布尔曲面对象
                    if current_bool_surface == None:
                        current_bool_surface = JCDBoolSurface()
                        current_bool_surface._load_from_dict(entity_data)
                    # 读取到最底层曲面
                    while True:
                        bool_operation_stack.append((entity_data['bool_type'], []))
                        entity_data = entity_data['sub_surface'] #取出子曲面的实际数据，矩阵信息被舍弃

                        if not 'bool_type' in entity_data:
                            break

                    if output_info:
                        print(f"创建新的布尔曲面，类型: {current_bool_surface.get_bool_type_name()}")

                if current_bool_surface is not None:
                    # 如果当前正在构建布尔曲面，则将此曲面添加为子曲面
                    # 确定布尔操作类型映射

                    # 将曲面添加到DAG中
                    surface_node_id = current_bool_surface.add_surface(entity_data)
                    bool_operation_stack[-1][1].append(surface_node_id)

                    if output_info:
                        print(f"  添加子曲面到布尔曲面，节点ID: {surface_node_id}")
                else:
                    # 普通曲面，正常处理
                    # 转换为数据类实例
                    entity_class = self.TYPE_CLASS_MAP.get(surface_type, JCDBaseData)
                    entity_instance = entity_class.from_dict(entity_data)

                    # 保存到列表
                    self.objects.append(entity_instance)

                    if output_info:
                        # 打印摘要
                        print_entity_summary(entity_data)

            # 处理可能未闭合的布尔曲面
            if current_bool_surface is not None:
                self.objects.append(current_bool_surface)
                if output_info:
                    print(f"布尔曲面处理完成，添加到对象列表")
                    current_bool_surface.print_dag_structure()

        if output_info:
            # 打印总体统计
            # 将对象转换回字典格式以便与现有的print函数兼容
            objects_as_dict = [obj.to_dict() for obj in self.objects]
            print_overall_summary(objects_as_dict)

        return True

    def saveAsTXTFile(
        self,
        save_txt_file_path: str,
        overwrite: bool = False,
    ) -> bool:
        """保存为文本文件

        Args:
            save_txt_file_path: 保存路径
            overwrite: 是否覆盖

        Returns:
            是否成功
        """
        if len(self.objects) == 0:
            print('[ERROR][JCDLoader::saveAsTXTFile]')
            print('\t valid data not found!')
            return False

        if os.path.exists(save_txt_file_path):
            if not overwrite:
                return True

            removeFile(save_txt_file_path)

        createFileFolder(save_txt_file_path)

        # 转换为字典格式
        objects_as_dict = [obj.to_dict() for obj in self.objects]
        save_entities_to_text(objects_as_dict, save_txt_file_path)

        return True

    def get_by_type(self, surface_type: SurfaceType) -> List[JCDBaseData]:
        """根据类型获取对象

        Args:
            surface_type: 曲面类型

        Returns:
            指定类型的对象列表
        """
        return [obj for obj in self.objects if obj.surface_type == surface_type]

    def get_curves(self) -> List[JCDCurve]:
        """获取所有曲线"""
        return [obj for obj in self.objects if isinstance(obj, JCDCurve)]

    def get_surfaces(self) -> List[JCDSurface]:
        """获取所有曲面"""
        return [obj for obj in self.objects if isinstance(obj, JCDSurface)]

    def get_diamonds(self) -> List[JCDDiamond]:
        """获取所有钻石"""
        return [obj for obj in self.objects if isinstance(obj, JCDDiamond)]

    def get_font_surfaces(self) -> List[JCDFontSurface]:
        """获取所有字体面片"""
        return [obj for obj in self.objects if isinstance(obj, JCDFontSurface)]

    def get_visible_objects(self) -> List[JCDBaseData]:
        """获取所有可见对象"""
        return [obj for obj in self.objects if not obj.hide]

    def get_hidden_objects(self) -> List[JCDBaseData]:
        """获取所有隐藏对象"""
        return [obj for obj in self.objects if obj.hide]

    def get_overall_bounding_box(self):
        """获取整体边界框

        Returns:
            (min_point, max_point) 或 None
        """
        import numpy as np

        all_min_points = []
        all_max_points = []

        for obj in self.objects:
            bbox = obj.get_bounding_box()
            if bbox is not None:
                min_pt, max_pt = bbox
                all_min_points.append(min_pt)
                all_max_points.append(max_pt)

        if not all_min_points:
            return None

        overall_min = np.min(np.array(all_min_points), axis=0)
        overall_max = np.max(np.array(all_max_points), axis=0)

        return overall_min, overall_max

    def renderAllData(self) -> bool:
        print(len(self.get_surfaces()))
        groups = [
            (self.get_curves(), [1.0, 0.0, 0.0]),      # 红色曲线
            (self.get_surfaces(), [0.0, 1.0, 0.0]),    # 绿色曲面
            (self.get_diamonds(), [1.0, 0.84, 0.0]),   # 金色钻石
        ]
        renderMultipleGroups(groups)
        return True

    def print_summary(self):
        """打印摘要信息"""
        print(f"\n{'='*60}")
        print(f"JCD文件摘要")
        print(f"{'='*60}")
        print(f"总对象数: {len(self.objects)}")
        print(f"可见对象: {len(self.get_visible_objects())}")
        print(f"隐藏对象: {len(self.get_hidden_objects())}")

        print(f"\n类型分布:")
        from collections import Counter
        type_counter = Counter(obj.surface_type for obj in self.objects)
        for surf_type, count in type_counter.items():
            print(f"  {surf_type}: {count}")
        
        # 打印布尔曲面的详细信息
        bool_surfaces = self.get_by_type(SurfaceType.BOOL_SURFACE)
        if bool_surfaces:
            print(f"\n布尔曲面详情:")
            for i, bool_surf in enumerate(bool_surfaces, 1):
                print(f"  布尔曲面 {i}:")
                print(f"    类型: {bool_surf.get_bool_type_name()}")
                print(f"    曲面数量: {bool_surf.get_surface_count()}")
                print(f"    根节点ID: {bool_surf.get_root_node_id()}")
                print(f"    隐藏状态: {bool_surf.hide}")

        # 边界框
        bbox = self.get_overall_bounding_box()
        if bbox:
            min_pt, max_pt = bbox
            size = max_pt - min_pt
            print(f"\n整体边界框:")
            print(f"  最小点: [{min_pt[0]:.2f}, {min_pt[1]:.2f}, {min_pt[2]:.2f}]")
            print(f"  最大点: [{max_pt[0]:.2f}, {max_pt[1]:.2f}, {max_pt[2]:.2f}]")
            print(f"  尺寸: [{size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}]")

        print(f"{'='*60}\n")
    
    def get_bool_surfaces(self) -> List[JCDBoolSurface]:
        """获取所有布尔曲面"""
        return [obj for obj in self.objects if isinstance(obj, JCDBoolSurface)]
    
    def render_bool_surfaces(self) -> bool:
        """渲染布尔曲面的DAG结构"""
        bool_surfaces = self.get_bool_surfaces()
        if not bool_surfaces:
            print("没有找到布尔曲面")
            return False
        
        print(f"渲染 {len(bool_surfaces)} 个布尔曲面的DAG结构:")
        for i, bool_surf in enumerate(bool_surfaces, 1):
            print(f"\n布尔曲面 {i}:")
            bool_surf.print_dag_structure()
        
        return True
