import os
from typing import Union, List

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
from jcd_manage.Data import (
    JCDCurve, JCDSurface, JCDDiamond, JCDFontSurface, 
    JCDGuideLine, JCDBoolSurface, JCDQuadType, JCDBaseData
)
from jcd_manage.Method.io import read_by_surface_type, save_entities_to_text
from jcd_manage.Method.info import print_entity_summary, print_overall_summary
from jcd_manage.Method.path import createFileFolder, removeFile



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

                # 转换为数据类实例
                entity_class = self.TYPE_CLASS_MAP.get(surface_type, JCDBaseData)
                entity_instance = entity_class.from_dict(entity_data)

                # 保存到列表
                self.objects.append(entity_instance)

                if output_info:
                    # 打印摘要
                    print_entity_summary(entity_data)

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
