import os,datetime
from datetime import date, timedelta
import shutil
import argparse

def copy_md_files(src_dir, dst_dir):
    # 检查源目录是否存在
    if not os.path.exists(src_dir):
        print(f"错误：源目录 '{src_dir}' 不存在")
        return False
    
    # 遍历源目录中的所有文件
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.md'):
                # 获取源文件的完整路径
                src_file_path = os.path.join(root, file)
                # 计算相对于源目录的相对路径
                relative_path = os.path.relpath(root, src_dir)
                # 构建目标目录路径，保持原有结构
                if relative_path == '.':
                    dst_file_dir = dst_dir
                else:
                    dst_file_dir = os.path.join(dst_dir, relative_path)
                
                # 创建目标目录（如果不存在）
                os.makedirs(dst_file_dir, exist_ok=True)
                # 构建目标文件的完整路径
                dst_file_path = os.path.join(dst_file_dir, file)
                
                try:
                    # 复制文件，保留元数据（修改时间等）
                    shutil.copy2(src_file_path, dst_file_path)
                    print(f"已复制: {src_file_path} -> {dst_file_path}")
                except Exception as e:
                    print(f"复制文件失败 {src_file_path}: {e}")
    print("操作完成！")
    return True

def main():

    source = 'C:\Software\database\ob\\0projects'
    destination = 'C:\Software\database\obsidian_bak_for_python\\'
    today = datetime.datetime.now().strftime('%Y%m%d')
    bak_folder_name = "obsidian_bak_" + today
    daily_bak_full_path = destination+bak_folder_name
    print(daily_bak_full_path)
    if not os.path.exists(daily_bak_full_path):
        # 创建文件夹（若父目录不存在会报错）
        os.mkdir(daily_bak_full_path)
        print(f"文件夹 {daily_bak_full_path} 已创建")
    
    # 执行复制操作
    copy_md_files(source, daily_bak_full_path)

if __name__ == "__main__":
    main()