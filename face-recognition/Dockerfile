FROM stpass/base_face

ENV server_port=5001

COPY face_compare.py ./face_compare.py

expose ${server_port}

CMD [ "python","./face_compare.py" ]
