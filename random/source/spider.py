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

def _get_value_from_dict(dict_map, key):
    '''从字典中获取指定key的value
    '''
    if type(dict_map) is not dict:
        raise Exception("Not a dict: "+ str(dict_map))
    if key not in dict_map or dict_map[key] is None:
        return ""
    else:
        return dict_map[key]

def _get_area_params(area_map):
    a_name = _get_value_from_dict(area_map, 'name')
    a_id = _get_value_from_dict(area_map, 'id')
    extra = _get_value_from_dict(area_map, 'extra')
    suffix = _get_value_from_dict(area_map, 'suffix')
    code = _get_value_from_dict(area_map, 'code')
    area_name = a_name + extra + suffix
    return a_id, area_name, code

def _get_provinces():
    '''查询所有省份,返回编码和全称[{'id': 13, 'pre_name': '安徽省', 'code': '340000', 'url': 'http://xxx/dic/districts?parentId=13'}]
    '''
    conf = load_conf()
    base_url = conf["url"]
    url = base_url + "0"
    provinces = get_data(url)
    results = []
    for p in provinces:
        r = {}
        p_id, pre_name, code = _get_area_params(p)
        r['id'] = p_id
        r['pre_name'] = pre_name
        r['code'] = code
        r['url'] = base_url + str(p_id)
        results.append(r)
    return results, base_url

def _get_citys(base_url ,url, province_name):
    '''查询指定省份下的所有城市[{'id': 226, 'pre_name': '安徽省安庆市', 'code': '340800', 'url': 'http://***/dic/districts?parentId=226'}]
    '''
    citys = get_data(url)
    results = []
    for c in citys:
        r = {}
        c_id, pre_name, code = _get_area_params(c)
        r['id'] = c_id
        r['pre_name'] = province_name + pre_name
        r['code'] = code
        r['url'] = base_url + str(c_id)
        results.append(r)
    return results

def _get_districts(url, city_name):
    '''查询指定城市下所有的县区{'340403': '安徽省淮南市田家庵区'}
    '''
    districts = get_data(url)
    results = {}
    for d in districts:
        r = {}
        d_id, d_name, code = _get_area_params(d)
        results[code] = city_name + d_name
    return results

def test():
    ps, base_url = _get_provinces()
    anhui = ps[12]
    anhuis = _get_citys(base_url, anhui['url'], anhui['pre_name'])
    huainan = anhuis[3]
    print(huainan)
    huainans = _get_districts(huainan['url'], huainan['pre_name'])
    print(huainans)

def main():
    results = {}
    provinces, base_url = _get_provinces()
    for p in provinces:
        citys = _get_citys(base_url, p['url'], p['pre_name'])
        for c in citys:
            districts = _get_districts(c['url'], c['pre_name'])
            if districts == {}:
                districts[c['code']] = c['pre_name']
            results = {**results, **districts}
    save_json(results)

if __name__ == '__main__':
    main()