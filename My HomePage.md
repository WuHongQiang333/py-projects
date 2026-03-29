---
ModifyDate: 2026年03月29日 19:37
CreateDate: 2025年07月15日 11:09
---
```dataviewjs
// 读取统计结果
try {
    // 获取Obsidian库路径，这里会自动获取。
    const vaultPath = app.vault.adapter.basePath;
    // 构建统计文件路径（用户主目录下的obsidian_stats文件夹）这里使用的是相对路径
    const today = moment().format('YYYYMMDD');
    const statsPath = `attachments/9_others/now.json`;
    
    // 使用app.vault.adapter.read读取外部文件
    const statsContent = await app.vault.adapter.read(statsPath);
    const data = JSON.parse(statsContent);
    const time3 = data.timestamp.match(/\d{2}:\d{2}:\d{2}/)
    const file_num = data.summary.files_new+data.summary.files_unchanged+data.summary.files_modified  
    
    dv.paragraph( `# 📊 今日统计 · ${data.date} ${moment().format('dddd')} | 统计时间：${time3}`);
    dv.paragraph( `**<font color="BlueGreen">共 ${file_num} 篇文章 | 总计 ${data.summary.total_chars.toLocaleString()} 字符 ${data.summary.total_lines.toLocaleString()} 行</font>**`);
    dv.paragraph(`**新增文件 ${data.summary.files_new.toLocaleString()} 篇 | 修改文件 ${data.summary.files_modified.toLocaleString()} 篇 | 新增字符: ${data.summary.total_added.toLocaleString()} | 删除字符: ${data.summary.total_deleted.toLocaleString()} | 新增行数 ${data.summary.total_added_lines.toLocaleString()} | 删除行数 ${data.summary.total_deleted_lines.toLocaleString()} | 净增字符: ${(data.summary.total_added - data.summary.total_deleted).toLocaleString()}**`);

     let idx=1; 
    const filesWithChanges = Object.entries(data.file_stats)
        .filter(([file, stats]) => stats.added_chars > 0 || (stats.deleted_chars > 0 ))  
        .sort((a, b) => b[1].added_chars - a[1].added_chars)
    filesWithChanges.forEach(([md_file,stats]) => {
        const diff = `${stats.diff_content.toLocaleString()}`;
        const cur_page = dv.pages()
            .where(p => md_file.includes(p.file.name))
            .first();
        dv.paragraph(`${idx} 📚 ${cur_page.file.link} | 新增字符 ${stats.added_chars} | 删除字符 ${stats.deleted_chars} | 新增行数 ${stats.added_lines} | 删除行数 ${stats.deleted_lines} | 具体修改如下:`);
        dv.paragraph(`${diff}`);
        idx +=1 ;
        })
} catch (error) {
    dv.paragraph("错误信息: " + error.message);
}
```


# 1 最近修改的 10 个文件
```dataviewjs
// 获取所有文件，按修改时间倒序排列，并限制数量
let files = dv.pages().sort(p => p.file.mtime, 'desc').limit(10);
// 用于跟踪上一个文件的修改日期
let lastDate = null;
// 创建容器来存放最终输出的元素
let output = [];
for (let page of files) {
    // 格式化当前文件的修改日期（仅日期部分，用于比较）
    let currentDate = moment(Number(page.file.mtime)).format('YYYY-MM-DD');
    // 如果当前文件的日期与上一个文件的日期不同，且不是第一个文件，则在输出数组中加入一个空行
    if (lastDate !== null && currentDate !== lastDate) {
        output.push(dv.el('p', '🌥 New Day')); // 插入一个空段落作为分隔行
    }
    // 更新记录的上一个日期
    lastDate = currentDate;
    // 将当前文件的信息（带格式的日期时间和链接）加入输出数组
    output.push(
        dv.el('p', '🗓' + moment(Number(page.file.mtime)).format('dddd MM-DD HH:mm') + '    >> ' + page.file.link
        )
    );
}
// 将所有元素渲染到页面
dv.span(output);
```
# 2 最近创建的 10 个文件
```dataviewjs
dv.list( dv.pages(``)
       .sort(p=>p.file.ctime,'desc')
       .limit (10)
       .map(p=>moment(Number(p.file.ctime)).format('MM-DD HH:mm')+' >> '+p.file.link)
       )
```

# 3 task

```dataviewjs
    dv.table(["Task","Name"],
        dv.pages("-#闪念胶囊 and -#稍后读")
        .sort(p=>p.file.mtime,'desc')
        .file.tasks.where(t => !t.completed)
        .limit(10)
        .map(b => ["[ ] - " + b.text,b.link])
    )

```


