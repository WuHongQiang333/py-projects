#!/usr/bin/env python3
"""
Obsidian笔记每日编辑量统计脚本
功能：对比今日笔记文件夹与昨日备份文件夹，统计每个文件的新增字符数和删除字符数
作者：根据用户需求编写
日期：2025-09-24
"""

import os,datetime
import json
import difflib
from difflib import Differ
from datetime import datetime, timedelta, date
import sys,re
from pathlib import Path
from colorama import Fore, Back, Style, init

def clean_markdown_content(content):
    # 去除前面的font matter
    pattern = r'^---[\s\S]*?---\s*'
    new_content = re.sub(pattern, '', content, count=1, flags=re.MULTILINE)
    # 去除空行
    lines = new_content.split('\n')
    new_lines = [line for line in lines if line.strip()]
    #print("lines : ",lines)
    res = '\n'.join(new_lines) #传入列表的时候，每个元素以换行符连接
    #print("content : ", content) 
    return res

def calculate_text_diff(old_content, new_content):
    # 清理内容
    old_cleaned = clean_markdown_content(old_content)
    new_cleaned = clean_markdown_content(new_content)
    old_cleaned_lines = old_cleaned.splitlines()
    new_cleaned_lines = new_cleaned.splitlines()

    differ = difflib.Differ()
    result = differ.compare(old_cleaned_lines, new_cleaned_lines)
    # 让修改的内容在obsidian上面以代码形式呈现，不然会出现渲染
    diff_content = "```\n"
    for line in result:
        if line.startswith('- '):
            # 红色显示被删除的行
            print(Fore.RED + line + Fore.RESET)
            diff_content = diff_content + '🔴' + line +"\n"
        elif line.startswith('+ '):
            # 绿色显示新增的行
            print(Fore.GREEN + line + Fore.RESET)
            diff_content = diff_content + '🟢' + line +"\n"
        elif line.startswith('? '):
            # 蓝色显示差异位置标记
            print(Fore.BLUE + line + Fore.RESET)
            diff_content = diff_content + '🔵' + line +"\n"
    diff_content = diff_content + "```"
    # 使用difflib计算差异
    # 如果需要统计的是字符串的差异，应该传入的是整个文本
    matcher = difflib.SequenceMatcher(None, old_cleaned, new_cleaned)
    added_chars = 0
    deleted_chars = 0
    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        
        if tag == 'replace':
            # 替换操作：旧文本被新文本替换
            deleted_chars += (i2 - i1)
            added_chars += (j2 - j1)
        elif tag == 'delete':
            deleted_chars += (i2 - i1)
        elif tag == 'insert':
            # 插入操作
            added_chars += (j2 - j1)
        elif tag == 'equal':
            # 相等部分，无需处理
            pass
    # 如果需要统计的是每一行的差异，应该传入的是以行为分割的列表
    matcher = difflib.SequenceMatcher(None, old_cleaned_lines, new_cleaned_lines)
    added_chars_lines = 0
    deleted_chars_lines = 0
    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        
        if tag == 'replace':
            # 替换操作：旧文本被新文本替换
            deleted_chars_lines += (i2 - i1)
            added_chars_lines += (j2 - j1)
        elif tag == 'delete':
            deleted_chars_lines += (i2 - i1)
        elif tag == 'insert':
            # 插入操作
            added_chars_lines += (j2 - j1)
        elif tag == 'equal':
            # 相等部分，无需处理
            pass
    
    return added_chars, deleted_chars, added_chars_lines, deleted_chars_lines, diff_content

def get_content(i_file_path) :
    f1 = open(i_file_path, 'r', encoding='utf-8')
    current_content = f1.read()
    f1.close()
    return current_content

def compare_folders(current_dir, backup_dir):
    results = {}
    mask_folders = ["attachments","attenchment",".obsidian",".trash","trash","脚本review"]
    if not os.path.exists(backup_dir):
        print(f"警告：备份目录不存在: {backup_dir}")
        return results
    # 遍历当前目录中的所有markdown文件

    work_path = Path(current_dir)
    back_path = Path(backup_dir)
    md_files = list(work_path.rglob("*.md"))
    back_md_files = list(back_path.rglob("*.md"))
    #print("md_files :", md_files)

    new_md_files = []
    for idx,elm in enumerate(md_files) :
        path_elm = str(elm).split('\\')
        if not (set(path_elm) & set(mask_folders)) : 
            new_md_files.append(elm)
        else :
            pass
            #print("文件",elm.name,"位于隐藏文件夹中，文件路径：",str(elm))
    print("一共将",len(md_files)-len(new_md_files),"个文件过滤") 



    work_file_basename_list = [elm.name for elm in md_files]
    back_file_basename_list = [elm.name for elm in back_md_files]
    #print("work dir md_files :", work_file_basename_list)
    #print("backup dir md_files :", back_file_basename_list)
    add_files = 0
    total_chars = 0
    total_lines = 0
    for idx,elm in enumerate(new_md_files,start=1) :
        #print("正在处理第",idx,"个文件，文件名：",elm.name)
        added_chars = 0
        deleted_chars = 0
        added_chars_lines = 0
        deleted_chars_lines = 0
        file_status = ""
        exist_same_file_flag = 0
        diff_content = []
        current_content = get_content(str(elm))
        total_chars += len(clean_markdown_content(current_content))
        total_lines += len(clean_markdown_content(current_content).splitlines())
        #print("current_content:",current_content)
        for elm2 in back_md_files :
            if str(elm.name) == str(elm2.name) :
                #print("命中文件：",elm.name,"开始比较")
                exist_same_file_flag = 1
                backup_content = get_content(str(elm2))
                #print(backup_content)
                # 计算差异
                added_chars, deleted_chars, added_chars_lines, deleted_chars_lines, diff_content = calculate_text_diff(backup_content, current_content)
                file_status = "modified" if (added_chars >0 or deleted_chars >0) else "unchanged"
        if exist_same_file_flag == 0 :
            # 新文件，所有内容都算作新增
            add_files += 1
            print("今日新建文件",elm.name)
            added_chars = len(clean_markdown_content(current_content))
            added_chars_lines = len(clean_markdown_content(current_content).splitlines())
            file_status = "new"
            diff_content.append(current_content)
        
        results[elm.name] = {
            'added_chars': added_chars,
            'deleted_chars': deleted_chars,
            'added_lines': added_chars_lines,
            'deleted_lines': deleted_chars_lines,
            'status': file_status,
            'current_path': str(elm),
            'diff_content' : diff_content
        }
    print("一共新增",add_files,"个文件")

    return total_chars,total_lines,results

def save_results_to_json(total_chars, total_lines, results, output_path):
    """
    将结果保存为JSON文件
    """
    # 准备给Dataview使用的数据格式
    dv_data = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'summary': {
            'total_chars': total_chars,
            'total_lines': total_lines,
            'total_added': sum(stats['added_chars'] for stats in results.values()),
            'total_deleted': sum(stats['deleted_chars'] for stats in results.values()),
            'total_added_lines': sum(stats['added_lines'] for stats in results.values()),
            'total_deleted_lines': sum(stats['deleted_lines'] for stats in results.values()),
            'files_modified': len([stats for stats in results.values() if stats['status'] == 'modified']),
            'files_unchanged': len([stats for stats in results.values() if stats['status'] == 'unchanged']),
            'files_new': len([stats for stats in results.values() if stats['status'] == 'new'])
        },
        'file_stats': results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dv_data, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {output_path}")

def get_obsidian_json(backup_dir,output_dir):
    vault = "C:\Software\database\ob\\0projects"
    print(f"当前笔记库: {vault}，对比备份文件夹: {backup_dir}")
    
    if not os.path.exists(backup_dir):
        print(f"文件夹 {backup_dir} 不存在。退出产生json文件")
        return 0
    # 对比文件夹
    total_chars, total_lines, results = compare_folders(vault, backup_dir)
    
    if results:
        # 保存结果
        save_results_to_json(total_chars, total_lines, results, output_dir)
        
        # 打印摘要
        total_added = sum(stats['added_chars'] for stats in results.values())
        total_deleted = sum(stats['deleted_chars'] for stats in results.values())
        total_added_lines = sum(stats['added_lines'] for stats in results.values())
        total_deleted_lines = sum(stats['deleted_lines'] for stats in results.values())

        print(f"\n📊 今日编辑统计摘要:")
        print(f"   新增字符数: {total_added}")
        print(f"   删除字符数: {total_deleted}")
        print(f"   新增行数: {total_added_lines}")
        print(f"   删除行数: {total_deleted_lines}")
        print(f"   净增字符数: {total_added - total_deleted}")
        print(f"   涉及文件数: {len(results)}")
    else:
        print("未找到需要统计的文件差异")

if __name__ == "__main__":
    backup_dir = "C:\Software\database\obsidian_bak_for_python\obsidian_bak_"
    today = date.today().strftime('%Y%m%d')

    output_dir= "C:\Software\database\ob\\0projects\\attachments\9_others\daily_" + today + ".json"
    output_dir_3days_before = "C:\Software\database\ob\\0projects\\attachments\9_others\daily_3day_before.json"
    output_dir_7days_before = "C:\Software\database\ob\\0projects\\attachments\9_others\daily_7day_before.json"
    output_dir_15days_before= "C:\Software\database\ob\\0projects\\attachments\9_others\daily_15day_before.json"
    output_dir_30days_before= "C:\Software\database\ob\\0projects\\attachments\9_others\daily_30day_before.json"

    date_3days_before = (date.today() - timedelta(days=3)).strftime('%Y%m%d')
    date_7days_before = (date.today() - timedelta(days=7)).strftime('%Y%m%d')
    date_15days_before = (date.today() - timedelta(days=15)).strftime('%Y%m%d')
    date_30days_before = (date.today() - timedelta(days=30)).strftime('%Y%m%d')
    print(date_3days_before)
    get_obsidian_json(backup_dir+today,output_dir)
    get_obsidian_json(backup_dir+date_3days_before,output_dir_3days_before)
    get_obsidian_json(backup_dir+date_7days_before,output_dir_7days_before)
    get_obsidian_json(backup_dir+date_15days_before,output_dir_15days_before)
    get_obsidian_json(backup_dir+date_30days_before,output_dir_30days_before)