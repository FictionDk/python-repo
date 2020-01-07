# -*- coding: utf-8 -*-

import random
from datetime import date
from datetime import timedelta
from random_area import District
from chinesename import ChineseName

class Person(object):
    """docstring for Person"""
    def __init__(self):
        super(Person, self).__init__()
        self._sexs = ["boy","girl"]
        self._chinesename = ChineseName()
        self._district = District()
        self._weights = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
        self._results = [1,0,'X',9,8,7,6,5,4,3,2]

    def _random_birthday(self):
        current_date = date.today()
        rand_max_date = date(current_date.year - 19, 12, 30)
        rand_min_date = date(current_date.year - 54, 1, 1)

        rand_days = random.randint(1,(rand_max_date - rand_min_date).days)
        rand_data = rand_min_date + timedelta(rand_days)
        return rand_data

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
        person_birthday = self._random_birthday()
        bodycode = area_code + person_birthday.strftime('%Y%m%d') + self._sex_code(person_sex)
        idcard_id = bodycode + self._check_code(bodycode)

        return person_name,person_sex,idcard_id,area_name,person_birthday.strftime('%Y-%m-%d')

def main():
    person = Person()
    p_name,p_sex,p_id,p_area,p_birth = person.get_person()
    print(p_name,"|",p_sex,"|",p_id,"|",p_area,"|",p_birth)

if __name__ == '__main__':
    main()
