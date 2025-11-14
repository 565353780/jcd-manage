import os
import numpy as np
from typing import Union

class JCDLoader(object):
    def __init__(self, jcd_txt_file_path: Union[str, None]=None) -> None:
        if jcd_txt_file_path is not None:
            self.loadTXTFile(jcd_txt_file_path)
        return

    def loadTXTFile(self, jcd_txt_file_path: str) -> bool:
        if not os.path.exists(jcd_txt_file_path):
            print('[ERROR][JCDLoader::loadTXTFile]')
            print('\t jcd txt file not exist!')
            print('\t jcd_txt_file_path:', jcd_txt_file_path)
            return False

        with open(jcd_txt_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(lines)
        return True
