import re

def process_md_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'^---[\s\S]*?---\s*'
    new_content = re.sub(pattern, '', content, count=1, flags=re.MULTILINE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    # 示例用法：修改为你的文件路径
    input_md = 'C:\Software\database\obsidian_bak_for_python\pro\d1581家用服务器配置.md'
    output_md = 'output.md'
    process_md_file(input_md, output_md)