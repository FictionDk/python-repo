FROM python:3.6

COPY requirements.txt ./
COPY pack /root/packs

# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip \
  && pip install --no-index  --find-links=/root/packs -r requirements.txt \
  && rm -rf /root/packs

# docker build -t stpass/base_face:1.0 .
