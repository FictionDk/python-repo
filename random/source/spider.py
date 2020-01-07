# -*- coding: utf-8 -*-
import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFFILE = os.path.join(BASE_DIR, "conf.json")

def get_data(url):
    result = requests.get(url)
    if result.ok:
        return result.json().get("data")
    else: 
        raise Exception("Get date from failed ,url = ",url)

def load_conf():
    with open(CONFFILE, "r", encoding="utf-8") as f:
        conf = json.loads(f.read())
    return conf

def save_json(dct):
    with open("district.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(dct, ensure_ascii=False, indent="\t"))

def set_whole_spell(district_list,name):
    for district in district_list:
        district["preName"] = _get_value_from_dict(district,"preName") + name
    return district_list

# 从字典中获取指定key的value
def _get_value_from_dict(dict_map,key):
    if type(dict_map) is not dict:
        raise Exception("Not a dict: "+ str(dict_map))
    if key not in dict_map or dict_map[key] is None:
        return ""
    else:
        return dict_map[key]

if __name__ == '__main__':
    conf = load_conf()
    base_url = conf["url"]
    url = base_url + "21"
    district_list = []
    citys = get_data(url)
    province_full_name = "广西壮族自治区"
    for city in citys:
        current_list = []
        url = base_url + str(city["id"])
        extra = city["extra"] if city["extra"] is not None else ""
        suffix = city["suffix"] if city["suffix"] is not None else ""
        preName = province_full_name + city["name"] + extra + suffix
        current_list += get_data(url)
        current_list = set_whole_spell(current_list,preName)
        district_list += current_list

    district_map_list = []
    for district in district_list:
        preName = district["preName"] if district["preName"] is not None else ""
        extra = district["extra"] if district["extra"] is not None else ""
        suffix = district["suffix"] if district["suffix"] is not None else ""

        district_map = {}
        district_map["name"] = preName+ district["name"] + extra + suffix
        district_map["code"] = district["code"]

        district_map_list.append(district_map)

    save_json(district_map_list)
