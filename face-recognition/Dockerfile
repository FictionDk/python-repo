FROM stpass/base_face:1.1

ENV server_port=5001
ENV TZ=Asia/Shanghai

RUN mkdir -p "/root/assert"

COPY *.py /root/*.py

expose ${server_port}

CMD [ "python","/root/face_compare.py" ]
