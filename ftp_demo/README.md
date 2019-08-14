# ftplib 使用

### 使用样例DEMO
```
from ftplib import FTP

ftp = FTP()
ftp.set_debuglevel(2)
ftp.connect('192.168.20.250',8021)
ftp.login('www','wwwadmin021')
```


