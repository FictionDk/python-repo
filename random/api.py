# -*- coding: utf-8 -*-
from flask import Flask,jsonify,request
from core import RandomPerson

app = Flask(__name__)

@app.route('/random/person',methods=['GET'])
def random_person():
    area_code = request.args.get('area')
    builder = RandomPerson(area_code)
    p_name,p_sex,p_id,p_area,p_birth = builder.get_person()
    person = {"name": p_name, "id":p_id, "sex": p_sex, "area": p_area, "birthday": p_birth}
    return jsonify({"code":"0", "data": person})

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=10006)