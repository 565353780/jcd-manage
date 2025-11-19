import os

from jcd_manage.Config.constant import JCD_HEADER
from jcd_manage.Config.types import SurfaceType
from jcd_manage.Method.path import removeFile
from jcd_manage.Method.io import read_by_surface_type

def convertJCDFile(
    jcd_file_path: str,
    save_txt_file_path: str,
    overwrite: bool = False,
) -> bool:
    if os.path.exists(save_txt_file_path):
        if not overwrite:
            return True

        removeFile(save_txt_file_path)

    if not os.path.exists(jcd_file_path):
        print('[ERROR][::convertJCDFile]')
        print('\t jcd file not exist!')
        print('\t jcd_file_path:', jcd_file_path)
        return False

    jcd_file = open(jcd_file_path, 'rb')

    jcd_header_str = JCD_HEADER
    header = jcd_file.read(len(jcd_header_str)).decode('utf-8')

    if header != jcd_header_str:
        print(f'header error header: {header}')
        exit(1)

    while True:
        end_flag = jcd_file.read(1)
        if chr(end_flag[-1]) == ':':
            print("flag :, continue") #读取下一个物体
        elif chr(end_flag[-1]) == '#':
            print("flag #, end") #文件结束标志
            break
        elif chr(end_flag[-1]) == '%':
            print("bool flag %, previous bool surface end") #前一个bool曲面的结束标志
            continue
        else:
            print(f"file headerunkown data 1 bytes, unkown_data: {end_flag}")
            exit(0)

        print("=================================================================")
        meta_info = jcd_file.read(8)
        surface_type = SurfaceType(int.from_bytes(meta_info[0:1], 'little'))
        print(f"surface_type: {surface_type}")
        print(f"meta_info: {meta_info.hex()}")
        read_by_surface_type(jcd_file, surface_type)
        print("=================================================================\n")

    return True
