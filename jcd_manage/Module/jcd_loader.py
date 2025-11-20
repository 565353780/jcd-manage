import os
from typing import Union, List

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
'''
from jcd_manage.Data import (
    Curve, Surface, Diamond, FontSurface, 
    GuideLine, BoolSurface, QuadType
)
'''
from jcd_manage.Method.io import read_by_surface_type, save_entities_to_text
from jcd_manage.Method.info import print_entity_summary, print_overall_summary
from jcd_manage.Method.path import createFileFolder, removeFile



class JCDLoader(object):
    def __init__(
        self,
        jcd_file_path: Union[str, None]=None,
        output_info: bool = False,
    ) -> None:
        self.objects: List = []

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

                # 保存到列表
                self.objects.append(entity_data)

                if output_info:
                    # 打印摘要
                    print_entity_summary(entity_data)

        if output_info:
            # 打印总体统计
            print_overall_summary(self.objects)

        return True

    def saveAsTXTFile(
        self,
        save_txt_file_path: str,
        overwrite: bool = False,
    ) -> bool:
        if len(self.objects) == 0:
            print('[ERROR][JCDLoader::saveAsTXTFile]')
            print('\t valid data not found!')
            return False

        if os.path.exists(save_txt_file_path):
            if not overwrite:
                return True

            removeFile(save_txt_file_path)

        createFileFolder(save_txt_file_path)

        save_entities_to_text(self.objects, save_txt_file_path)

        return True
