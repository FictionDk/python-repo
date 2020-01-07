# -*- coding: utf-8 -*-

import json
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISTRICT_FILE = os.path.join(BASE_DIR, "source","district.json")

class District(object):
    """docstring for Districk"""
    def __init__(self):
        super(District, self).__init__()
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

def test():
    district = District()
    print(district.get_district())
