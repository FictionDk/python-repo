FROM python:3.7-alpine

ENV server_port=10006
ENV TZ=Asia/Shanghai

RUN mkdir -p "/root/source"
RUN mkdir -p "/root/config"

COPY requirements.txt ./
COPY *.py /root/
COPY source /root/source
COPY config /root/config

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests \
    && python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

expose ${server_port}

CMD [ "python","/root/api.py" ]
