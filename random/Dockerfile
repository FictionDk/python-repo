FROM python:3.7-alpine

ENV server_port=10006
ENV TZ=Asia/Shanghai

RUN mkdir -p "/root/source"

COPY requirements.txt ./
COPY *.py /root/
COPY source /root/source

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

expose ${server_port}

CMD [ "python","/root/api.py" ]
