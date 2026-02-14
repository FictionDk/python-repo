### 每天一次
1. 执行manage_commit,同步git commit记录到数据库，并根据commit内容取出issue更新gitlab
2. 登录gitlab任务看板,通过标签（start::dev、front::finished、backend::finished）批量更新状态
3. 执行manage_issue,更新issue列表

### 建议一周一次
1. 分析本轮(指定时间段)commit记录,输出本周开发进度，具体内容格式：
    - 本周（xxx - xxx）完成了x次提交，关联x个issue,完成x个issue开发（前端x个，后端x个），主要处理内容为:（将关联的issue.title、关联类型和关联次数提交给大模型进行总结,插入）

### 日汇总
1. 从commit中提取当天指定项目列表的提交记录，汇总提交总数和带issue的提交数量
2. 将带issue: author_name+message+issue_iid，并从issue-main中取出对应iid+title，以及未完成的数量（latest_status in ['待开发'，'开发中']）和当前日期提交给大模型
3. 汇总本日开发简报
