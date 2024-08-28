# [monitor.py](./monitor.py)

1. 内存监控程序
2. 系统随机启动

```
vi /etc/systemd/system/py_monitor.service

[Unit]
Description=Python Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python /root/monitor/check.py
WorkingDirectory=/root/monitor/
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target


systemctl start py_monitor.service
systemctl status py_monitor.service
systemctl enable py_monitor.service

日志查看: journalctl -u py_monitor.service -f
日志存储: /var/log/journal/
日志规则: /etc/systemd/journald.conf

```