# 文件简介
copy_ob_prj脚本用来复制一个目录里面的所有的md文件到另外一个备份文件夹，备份文件夹里的名称包含日期信息。  
python_obsidian脚本用来输出包含两个库之间的md文件差异的json文件，这个json文件后续会被obsidian的homepage插件读取。  

# 使用方法
copy_ob_prj脚本，每日运行一次，生成库文件的备份。  
python_obsidian脚本每5分钟运行一次，不断刷新json文件。  
在obsidian里面使用名为'Homepage'的插件，就'My HomePage.md'文档设置为homepage。  
'My HomePage.nmd'文档里面使用dataview语法来读取python_obsidian产生的json文件，需要安装dataview插件。  
进入阅读模式就可以看到渲染出来的效果了。
<img width="1126" height="747" alt="image" src="https://github.com/user-attachments/assets/2de4651e-556f-4971-bd7d-fd6e0f6b1f11" />



# up_link.py
用来更新obsidian vault里面的双向链接（标题），格式如[预览时显示的文本](<文档名称>#<链接的标题的名称>)。  
原理是遍历每一篇文档，在每一行里面寻找类似格式的文本，如果找到了就去对应文档里面拿到最新的标题列表信息。  
然后使用字符串对比工具，计算当前的标题和现在最新的标题列表中每一个标题的相似度，取最高相似度的标题作为将要用来替换<链接的标题的名称>。  
不会匹配对于文本和其他如图片的引用，举例文本链接中<链接的标题的名称>为类似<^sdfs>的字符串，所以只会对标题的双向链接起作用。

