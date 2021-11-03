# -*- coding: utf-8 -*-
from flask import Flask,jsonify,request
from core import RandomPerson
from pgsql import LabelUtils

app = Flask(__name__)

@app.route('/random/person',methods=['GET'])
def random_person():
    area_code = request.args.get('area')
    builder = RandomPerson(area_code)
    p_name,p_sex,p_id,p_area,p_birth = builder.get_person()
    person = {"name": p_name, "id":p_id, "sex": p_sex, "area": p_area, "birthday": p_birth}
    return jsonify({"code":"0", "data": person})

@app.route('/random/rfid/label',methods=['GET'])
def random_label():
    num = request.args.get('number')
    utils = LabelUtils()
    labels,end_num = utils.get_random_labels(num)
    return jsonify({"code":"0", "data": labels})


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=10006)