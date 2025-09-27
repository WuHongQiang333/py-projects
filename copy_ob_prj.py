import os
import shutil
import argparse

def copy_md_files(src_dir, dst_dir):
    """
    复制源目录中所有的 .md 文件到目标目录，保持目录结构不变
    
    Args:
        src_dir (str): 源目录路径
        dst_dir (str): 目标目录路径
    """
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
    # 设置命令行参数解析

    
    source = 'C:\Software\database\ob\\0projects'
    destination = 'C:\Software\database\obsidian_bak_for_python\pro'
    

    
    # 执行复制操作
    copy_md_files(source, destination)

if __name__ == "__main__":
    main()