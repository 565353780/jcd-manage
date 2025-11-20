from jcd_manage.Module.jcd_loader import JCDLoader

def demo():
    jcd_txt_file_path = '/Users/chli/Downloads/001_0002.jcd'
    output_info = True
    save_txt_file_path = '/Users/chli/Downloads/001_0002.txt'
    overwrite = True

    jcd_loader = JCDLoader(jcd_txt_file_path, output_info)
    jcd_loader.renderAllData()
    jcd_loader.saveAsTXTFile(save_txt_file_path, overwrite)
    return True
