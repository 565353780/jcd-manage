from jcd_manage.Module.jcd_convertor import convertJCDFile

def demo():
    jcd_file_path = "/Users/chli/Downloads/001_0001.jcd"
    save_txt_file_path = "/Users/chli/Downloads/001_0001.txt"
    overwrite = True

    convertJCDFile(jcd_file_path, save_txt_file_path, overwrite)
    return True
