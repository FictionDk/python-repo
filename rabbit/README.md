## Log Reciver

> App what get queue msg from rabbit auto  
> App is managed by nohup  

### pre commond
`pip3 install pika`

### start commond:  
`nohup python3 subscribe.py > revicer_log.log & echo $! > pidfile.txt`  

### end commond:
```
kill -9 `cat pidfile.txt`
```
