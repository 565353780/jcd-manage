#!/usr/bin/env python3
"""IGES加载器演示"""

from jcd_manage.Module.iges_loader import IGESLoader

def main():
    # 替换为你的IGES文件路径
    iges_file = "/Users/chli/Downloads/FeiShu/JCD/111/11.igs"
    
    print(f"正在加载IGES文件: {iges_file}")
    
    # 创建加载器
    loader = IGESLoader(iges_file)
    
    # 加载文件
    entities = loader.load()
    
    # 打印摘要
    loader.print_summary()
    
    print(f"\n成功加载 {len(entities)} 个实体")

if __name__ == "__main__":
    main()
