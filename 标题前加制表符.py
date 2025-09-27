import re

# 读取文本文件内容
file_path = 'C:/Software/thonny-4.1.4-windows-portable/py-projects/1.txt'  # 请将your_file_path.txt替换为您实际的文件路径
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 正则表达式匹配二级标题格式
regex_second_level = r'(\d+\.\d+)'
replacement_second_level = r'\t\1'  # 在匹配到的文本前添加一个制表符

# 替换匹配到的二级标题
new_content = re.sub(regex_second_level, replacement_second_level, content)

# 正则表达式匹配三级标题格式
regex_third_level = r'(\d+\.\d+\.\d+)'
replacement_third_level = r'\t\1'  # 在匹配到的文本前添加两个制表符

# 替换匹配到的三级标题
new_content = re.sub(regex_third_level, replacement_third_level, new_content)

# 将替换后的内容写入文件
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print('替换完成！')