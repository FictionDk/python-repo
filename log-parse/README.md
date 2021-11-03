# log4j日志格式解析

## demo.line:
```
2021-10-28 18:22:43.942 [XNIO-1 task-4] ERROR c.s.s.berrysup.core.config.MyErrorAttributesConfig - Error: {timestamp=2021-10-28 18:22:43, status=400, error=Bad Request, message=参数格式不正确或缺失,详情:特免血浆缺少免疫类型[vaccinationType],可选:[HEPATITIS_B|RABIES|TETANUS|ANTHRAX], path=/api/plasmacollect/save, deptNo=4509220353}
```

## 目标
剔除多余字符,将`{}`内的内容按对象存入内存并按需输出统计结果

## 步骤
1. 清洗数据,将数据按指定对象格式化
2. 根据已完成清洗数据按指定格式统计输出
