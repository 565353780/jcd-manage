from jcd_manage.Module.iges_loader import IGESLoader

def demo():
    iges_file_path = '/Users/chli/Downloads/FeiShu/JCD/111/11.igs'

    # 创建加载器并加载文件
    loader = IGESLoader(iges_file_path)
    entities = loader.load()

    # 打印摘要
    loader.print_summary()

    # 打印详细信息
    loader.print_details(max_entities=5)
