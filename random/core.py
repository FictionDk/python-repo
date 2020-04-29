# -*- coding: utf-8 -*-

import random
import os
import json
from datetime import date
from datetime import time
from datetime import timedelta
from datetime import datetime
from chinesename import ChineseName

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISTRICT_FILE = os.path.join(BASE_DIR, "source","district.json")

class RandomDistrict(object):
    """生成随机地区"""
    def __init__(self):
        super(RandomDistrict, self).__init__()
        self._districts = self._get_districts()

    def _get_districts(self):
        districts_json = {}
        with open(DISTRICT_FILE,'r+',encoding="utf-8") as f:
            districts_str = f.read()
            if len(districts_str) > 0:
                districts_json = json.loads(districts_str)
        return districts_json

    def get_district(self):
        return random.choice(self._districts)

class RandomTime(object):
    """生成随机时间"""

    def random_birthday(self, min_age = 19, max_age = 54):
        '''生成随机出生日期
        Args: 
            min_age: 最小随机年龄
            max_age: 最大随机年龄
        Returns:
            <class 'datetime.date'> 样式: 'yyyy-MM-dd'
        '''
        current_date = date.today()
        rand_max_date = date(current_date.year - min_age, 12, 30)
        rand_min_date = date(current_date.year - max_age, 1, 1)
        rand_days = random.randint(1,(rand_max_date - rand_min_date).days)
        rand_data = rand_min_date + timedelta(rand_days)
        return rand_data

    def random_datetime(self, rand_date = None, min_seconds = 0, max_seconds = 86400):
        '''生成随机日期时间
        Args: 
            rand_date: 随机日期
            min_seconds: 最大随机秒数
            max_seconds: 最大随机秒数
        Returns:
            <class 'datetime.datetime'> 样式: 'yyyy-MM-dd HH:mm:ss'
        '''
        if rand_date is None:
            rand_date = self.random_date()
        rand_seconds = timedelta(seconds=random.randint(min_seconds, max_seconds))
        return datetime.combine(rand_date, time.min) + rand_seconds

    def random_date(self, min_day = 0 , max_day = 20):
        '''生成小于当前日期随机间隔天数的日期
        Args: 
            min_day: 最小随机值
            max_day: 最大随机值
        Returns: 
            <class 'datetime.date'> 样式: 'yyyy-MM-dd'
        '''
        rand_days = random.randint(min_day, max_day)
        return date.today() - timedelta(rand_days)

class RandomPerson(object):
    """生成随机人物(姓名,性别,身份证,所在地,生日)"""
    def __init__(self):
        super(RandomPerson, self).__init__()
        self._sexs = ["boy","girl"]
        self._chinesename = ChineseName()
        self._district = RandomDistrict()
        self._timer = RandomTime()
        self._weights = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
        self._results = [1,0,'X',9,8,7,6,5,4,3,2]

    def _random_name(self):
        sex = random.choice(self._sexs)
        name = self._chinesename.getName(sex=sex)
        return name,sex

    def _random_area(self):
        district_dict = self._district.get_district()
        return district_dict["name"],district_dict["code"]

    # [身份证生成规则]顺序码,奇数为男,偶数为女
    def _sex_code(self,sex):
        code = random.randrange(0,998,2)
        if "boy" is sex:
            code += 1
        return str(code)

    def _check_code(self,bodycode):
        result = 0
        for i in range(0,len(bodycode)):
            result += int(bodycode[i]) * self._weights[i]
        result = result % 11
        return str(self._results[result])

    def get_person(self):
        area_name,area_code = self._random_area()
        person_name,person_sex = self._random_name()
        person_birthday = self._timer.random_birthday()
        bodycode = area_code + person_birthday.strftime('%Y%m%d') + self._sex_code(person_sex)
        idcard_id = bodycode + self._check_code(bodycode)
        return person_name,person_sex,idcard_id,area_name,person_birthday.strftime('%Y-%m-%d')

def main():
    person = RandomPerson()
    p_name,p_sex,p_id,p_area,p_birth = person.get_person()
    print(p_name,"|",p_sex,"|",p_id,"|",p_area,"|",p_birth)
    rt = RandomTime()
    rand_date = rt.random_date(max_day = 50)
    print(rand_date)
    print(rt.random_datetime(rand_date))
    print(type(rt.random_datetime(rand_date)))

if __name__ == '__main__':
    main()
