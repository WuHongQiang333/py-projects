#!/usr/bin/env python3


import subprocess
import os,time
from datetime import datetime, timedelta, date
import json
import shutil
import difflib
from difflib import Differ
import sys,re
from pathlib import Path
from colorama import Fore, Back, Style, init

def clean_markdown_content(content):
    # 去除前面的font matter
    pattern     = r'^---[\s\S]*?---\s*'
    new_content = re.sub(pattern, '', content, count      =1, flags=re.MULTILINE)
    lines       = new_content.split('\n')
    new_lines   = [line for line in lines if line.strip()]
    res         = '\n'.join(new_lines) #传入列表的时候，每个元素以换行符连接
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
            #print(Fore.RED + line + Fore.RESET)
            diff_content = diff_content + '🔴' + line +"\n"
        elif line.startswith('+ '):
            # 绿色显示新增的行
            #print(Fore.GREEN + line + Fore.RESET)
            diff_content = diff_content + '🟢' + line +"\n"
        elif line.startswith('? '):
            # 蓝色显示差异位置标记
            #print(Fore.BLUE + line + Fore.RESET)
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
    mask_folders = ["attachments","attenchment",".obsidian",".trash","trash","脚本review","Cubox0"]
    if not os.path.exists(backup_dir):
        print(f"警告：备份目录不存在: {backup_dir}")
        return results
    # 遍历当前目录中的所有markdown文件
    work_path     = Path(current_dir)
    back_path     = Path(backup_dir)
    md_files      = list(work_path.rglob("*.md"))
    back_md_files = list(back_path.rglob("*.md"))
    #print("md_files :", md_files)

    new_md_files = []
    for idx,elm in enumerate(md_files) :
        #path_elm = str(elm).split('\\') #如果是在win系统中运行脚本使用这个
        path_elm = str(elm).split('/') #如果是在linux系统中运行脚本使用这个
        if not (set(path_elm) & set(mask_folders)) : # 如果文件夹没有交集
            new_md_files.append(elm)
        else :
            pass
            #print("文件",elm.name,"位于隐藏文件夹中，文件路径：",str(elm))
    print("一共将",len(md_files)-len(new_md_files),"个文件过滤",flush=True) 


    work_file_basename_list = [elm.name for elm in md_files]
    back_file_basename_list = [elm.name for elm in back_md_files]
    #print("work dir md_files :", work_file_basename_list)
    #print("backup dir md_files :", back_file_basename_list)
    add_files   = 0
    total_chars = 0
    total_lines = 0
    for idx,elm in enumerate(new_md_files,start=1) :
        #print("正在处理第",idx,"个文件，文件名：",elm.name)
        added_chars          = 0
        deleted_chars        = 0
        added_chars_lines    = 0
        deleted_chars_lines  = 0
        file_status          = ""
        exist_same_file_flag = 0
        diff_content         = []
        current_content      = get_content(str(elm))
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
            added_chars       = len(clean_markdown_content(current_content))
            added_chars_lines = len(clean_markdown_content(current_content).splitlines())
            file_status       = "new"
            diff_content.append(current_content)
        
        results[elm.name] = {
            'added_chars'  : added_chars,
            'deleted_chars': deleted_chars,
            'added_lines'  : added_chars_lines,
            'deleted_lines': deleted_chars_lines,
            'status'       : file_status,
            'current_path' : str(elm),
            'diff_content' : diff_content
        }
    print("一共新增",add_files,"个文件",flush=True)

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
            'total_chars'        : total_chars,
            'total_lines'        : total_lines,
            'total_added'        : sum(stats['added_chars']   for stats in results.values()),
            'total_deleted'      : sum(stats['deleted_chars'] for stats in results.values()),
            'total_added_lines'  : sum(stats['added_lines']   for stats in results.values()),
            'total_deleted_lines': sum(stats['deleted_lines'] for stats in results.values()),
            'files_modified'     : len([stats for stats in results.values() if stats['status'] == 'modified']),
            'files_unchanged'    : len([stats for stats in results.values() if stats['status'] == 'unchanged']),
            'files_new'          : len([stats for stats in results.values() if stats['status'] == 'new'])
        },
        'file_stats': results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dv_data, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到: {output_path}",flush=True)

def get_obsidian_json(vault, backup_dir,o_json_file):

    print(f"当前笔记库: {vault}，对比备份文件夹: {backup_dir}",flush=True)
    
    if not os.path.exists(backup_dir):
        print(f"文件夹 {backup_dir} 不存在。退出产生json文件\n",flush=True)
        return 0
    # 对比文件夹
    total_chars, total_lines, results = compare_folders(vault, backup_dir)
    save_results_to_json(total_chars, total_lines, results, o_json_file)
    print_summary(results)
        
def print_summary(i_result):
    if i_result:
        # 打印摘要
        total_added         = sum(stats['added_chars']   for stats in i_result.values())
        total_deleted       = sum(stats['deleted_chars'] for stats in i_result.values())
        total_added_lines   = sum(stats['added_lines']   for stats in i_result.values())
        total_deleted_lines = sum(stats['deleted_lines'] for stats in i_result.values())

        print(f"\n📊 今日编辑统计摘要:",flush=True)
        print(f"   新增字符数: {total_added}",flush=True)
        print(f"   删除字符数: {total_deleted}",flush=True)
        print(f"   新增行数: {total_added_lines}",flush=True)
        print(f"   删除行数: {total_deleted_lines}",flush=True)
        print(f"   净增字符数: {total_added - total_deleted}",flush=True)
        print(f"   涉及文件数: {len(i_result)}",flush=True)
        print("===========================================\n\n",flush=True)
    else:
        print("未找到需要统计的文件差异",flush=True)
        print("===========================================\n\n",flush=True)



def send_restart_cmd():
    time.sleep(5)
    cmd = '/usr/bin/sshpass -p "whq258369" ssh wuhongqiang@192.168.3.14 "shutdown /r /f /t 0"'
    try:
        for i in range(5):
            with open(copy_obs_flag, "a") as f:
                f.write(f"{datetime.now().isoformat()}: {i+1}th Sending restart command \n")
            subprocess.run(cmd, shell=True, capture_output=False)
            time.sleep(2)
    except Exception as e:
        pass

def copy_md_files_to_date_dir(flag_file, source_dir, target_root_dir):
    """
    将指定目录下所有.md文件复制到以当天日期命名的目录中，目录已存在则跳过
    
    参数:
        source_dir (str): 源目录路径（存放要复制的md文件）
        target_root_dir (str): 目标根目录路径（日期目录会创建在此目录下）
    """

    today = date.today()
    if os.path.exists(flag_file) and today == date.fromtimestamp(os.path.getmtime(flag_file)):
        print("今日已执行过 copy_md_files_to_date_dir 任务，跳过")
        return
    else :
        try:
            os.makedirs(target_root_dir, exist_ok=True)
            print(f"成功创建目录: {target_root_dir}",flush=True)

            
            # 4. 遍历源目录，复制所有.md文件到目标目录
            copied_count = 0
            md_files = list(Path(source_dir).rglob("*.md"))
            #print(str(md_files))
            for file in md_files:
                shutil.copy2(file, target_root_dir)
                copied_count += 1
            # 5. 输出复制结果
            print(f"\n复制完成！共复制 {copied_count} 个md文件到 {target_root_dir}",flush=True)
            with open(flag_file, "w") as f:
            # 写入当前日期（可选，方便人工查看）
                f.write(f"Last run: {datetime.now().isoformat()}\n") 
                f.write(f"开始获取everyday写的数据，从1天前到7天前\n") 
                get_everyday_obs_diff()
                f.write(f"即将重启电脑以完成obsidian文件的更新\n") 
            #Based on the actual situation, decide whether to restart after copying the obs folder
            send_restart_cmd()
        except Exception as e:
            print(f"创建目录失败: {e}",flush=True)
            return   
        
        
        
def find_2_date_obs_diff( new_date, old_date, o_json_file):
    backup_dir1 = backup_dir + subdir_prefix + old_date
    backup_dir2 = backup_dir + subdir_prefix + new_date
    if not os.path.exists(backup_dir1):
        print(f"文件夹 {backup_dir1} 不存在。退出\n",flush=True)
        return 0
    if not os.path.exists(backup_dir2):
        print(f"文件夹 {backup_dir2} 不存在。退出\n",flush=True)
        return 0
    total_chars, total_lines, results = compare_folders(backup_dir2, backup_dir1)
    if results:
        save_results_to_json(total_chars, total_lines, results, o_json_file)
        print_summary(results)
        print(f"对比数据库， 日期: {new_date} 和 {old_date} \n",flush=True)
    

def get_everyday_obs_diff():
    for i in range(0,8) :
        find_2_date_obs_diff((date.today() - timedelta(days=i)).strftime('%Y%m%d'), (date.today() - timedelta(days=i+1)).strftime('%Y%m%d'), save_json_file_dir + f"{i+1}day_before.json")


if __name__ == "__main__":
    
    print("run timestamp:", datetime.now().isoformat())
    today               = date.today().strftime('%Y%m%d')
    # 每天保存md文件的备份放在这里
    backup_dir          = "/mnt/hp800g4_obs_data/obs_bak/"
    subdir_prefix       = "obs_bak_" # 子文件夹的前缀
    # win11中存储obs笔记的路径,你现在写的东西
    valut               = "/mnt/hp800g4_obs_data/0projects/"
    save_json_file_dir  = "/mnt/hp800g4_obs_data/0projects/attachments/9_others/"
    # 用来标记obs文件是否已经经过了复制
    copy_obs_flag       = "/tmp/copy_obs_flag.log"
    
    copy_md_files_to_date_dir(copy_obs_flag, valut, backup_dir+subdir_prefix+today)
    
    output_dir               = save_json_file_dir + "now.json"
    output_dir_3days_before  = save_json_file_dir + "daily_3day_before.json"
    output_dir_7days_before  = save_json_file_dir + "daily_7day_before.json"
    output_dir_15days_before = save_json_file_dir + "daily_15day_before.json"
    output_dir_30days_before = save_json_file_dir + "daily_30day_before.json"
    #昨天写了什么
    yestoday_json_file       = save_json_file_dir + "daily_yestoday.json"

    today              = date.today().strftime('%Y%m%d')
    yestoday           = (date.today() - timedelta(days=1 )).strftime('%Y%m%d')
    date_3days_before  = (date.today() - timedelta(days=3 )).strftime('%Y%m%d')
    date_7days_before  = (date.today() - timedelta(days=7 )).strftime('%Y%m%d')
    date_15days_before = (date.today() - timedelta(days=15)).strftime('%Y%m%d')
    date_30days_before = (date.today() - timedelta(days=30)).strftime('%Y%m%d')
    
    get_obsidian_json(valut, backup_dir+subdir_prefix+today              ,output_dir)
    get_obsidian_json(valut, backup_dir+subdir_prefix+date_3days_before  ,output_dir_3days_before)
    get_obsidian_json(valut, backup_dir+subdir_prefix+date_7days_before  ,output_dir_7days_before)
    get_obsidian_json(valut, backup_dir+subdir_prefix+date_15days_before ,output_dir_15days_before)
    get_obsidian_json(valut, backup_dir+subdir_prefix+date_30days_before ,output_dir_30days_before)
