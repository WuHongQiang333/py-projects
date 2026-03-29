import os,sys,re
import shutil,stat
from pathlib import Path
from Levenshtein import ratio

# ====================== 配置 ======================
VAULT_PATH = "/mnt/hp800g4_obs_data/0projects/"  # 改成你的库路径

def get_backlinks(vault_path):
    #匹配 (自定义链接名)[文件名#标题] 这种格式的链接
    pat0 = re.compile(r'\[([^\]]+)\]\(([^.]+\.md)\#([^\)]+)\)') 
    for i,md_file in enumerate(Path(vault_path).rglob("*.md")):
        print(f"正在处理第 {i+1} 个文件：{md_file}", flush=True)
        original_stat = os.stat(md_file)  # 获取原文件的访问和修改时间
        with open(str(md_file) + ".tmp", "w", encoding="utf-8") as f_out  :
            for line in open(md_file, "r", encoding="utf-8"):
                    if pat0.search(line):
                        #explain = pat0.search(line).group(1) #()自定义链接名
                        tar_file_name = pat0.search(line).group(2) #()里面的文本，通常是链接的标题
                        cur_heading   = pat0.search(line).group(3) #()里面的文本，通常是链接的标题
                        if not chk_string_text_link(cur_heading):
                            new_headings = get_newest_headings_of_mdfiles(tar_file_name)
                            simi, idx    = get_max_similarity_heading(cur_heading, new_headings)
                            if 1 > simi > theld :
                                new_heading = new_headings[idx]
                                replace_list.append([simi, fliter_heading_text(cur_heading), fliter_for_spacing(new_headings[idx])])
                                new_heading = new_headings[idx].replace(' ','%20')
                            else :
                                new_heading = cur_heading
                                attention_list.append([simi, fliter_heading_text(cur_heading), fliter_for_spacing(new_headings[idx])])
                            new_line = line.replace(cur_heading, new_heading)  # 替换链接标题
                            f_out.write(new_line)  # 替换标题文本并写入临时文件
                        else:
                            f_out.write(line)
                    else:
                        f_out.write(line)  # 非标题行直接写入临时文件
        shutil.move(str(md_file) + ".tmp", str(md_file))
        os.utime(str(md_file), (original_stat.st_atime, original_stat.st_mtime))
                        

def chk_string_text_link(heading_text) -> bool:
    # 这里可以根据实际情况调整正则表达式以匹配不同类型的链接
    pattern = re.compile(r'(\^[a-z0-9]+|page\=)') # 这里匹配文本链接或者pdf注释链接，定到pdf多少页
    if pattern.search(heading_text):
        return True
    else:
        return False

def fliter_heading_text(heading_text):
    # md文档读回的时候，空格会变成编码%20，这里把它去掉，方便后续的相似度计算
    res = heading_text.replace('%20', '')
    return res

def fliter_for_spacing(file_name):
    # 读取最新的标题列表的时候用这个函数把标题中的空格去掉，方便后续的相似度计算
    return file_name.replace(' ', '')

def get_max_similarity_heading(text0, list_headings):
    max_sim,max_idx = 0,0

    for idx,heading in enumerate(list_headings):
        sim = is_similar(fliter_heading_text(text0), fliter_for_spacing(heading))
        if sim > max_sim:
            max_sim, max_idx = sim, idx
    return max_sim, max_idx

def get_newest_headings_of_mdfiles(tar_file_name):
    headings = []
    max_sim  = 0
    max_file = None
    patttern = re.compile(r'^(#+)\s{1}(.*)')  # 匹配 Markdown 标题的正则表达式
    
    for i_file in Path(VAULT_PATH).rglob("*.md"):
        cur_simi = is_similar(Path(i_file).name,tar_file_name) 
        if cur_simi > max_sim :
            max_sim, max_file = cur_simi, i_file

    with open(max_file, "r", encoding="utf-8") as f:
        content = f.readlines()
    for line in content:
        if patttern.match(line):
            heading = patttern.match(line).group(2) #获取标题文本
            headings.append(heading)

    return headings

def is_similar(str1, str2):
    return ratio(str1, str2)

if __name__ == "__main__":
    # ====================== 主程序入口 ======================
    """当你在一篇文档里面使用了 [[文件名#标题]] 这种格式的链接，或者 (自定义链接名)[文件名#标题] 这种格式的链接，
    1. 运行这个脚本会自动把链接里面的标题更新成最新的标题。相似度高于80%的会被自动替换，低于80%的会被标记到注意列表中，供你手动检查。
    2. 可以通过传参的方式调整相似度阈值，例如 python up_link.py 0.9 表示只有相似度高于90%的才会被自动替换。
    """

    debug          = True
    replace_list   = []
    attention_list = []
    theld = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8 #相似度阈值，0.8表示80%的相似度以上才会被替换，低于这个值的会被标记到注意列表中

    get_backlinks(VAULT_PATH)
    print(f"\n===================== Replace Report =====================", flush=True)
    for it in sorted(replace_list,key=lambda x:x[0],reverse=True):
        print(f"相似度={it[0]:.2f} old={it[1]:<40} -> new={it[2]:<40}", flush=True)
    print(f"\n===================== Attention Report ===================", flush=True)
    for it in sorted(attention_list,key=lambda x:x[0],reverse=True):
        print(f"相似度={it[0]:.2f} old={it[1]:<40}-> new={it[2]:<40}", flush=True)
    