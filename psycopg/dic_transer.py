# -*- coding: utf-8 -*-
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# 打包后的环境
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

class ArgsNotNull(RuntimeError):
    pass

def get_full_filename(directory,filename=None):
    '''获取当前执行目录下的指定路径下的文件名
    Args:
        filename: 文件名,可为空,返回文件夹全路径
        directory: 目录名称
    Returns:
        返回文件的全路径
    Raises:
        ArgsNotNull: 参数不能为空
    '''
    if directory is None:
        raise ArgsNotNull("directory can not be None")
    dir_name = os.path.join(BASE_DIR,directory)

    # 确保目录存在
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if filename is None:
        return dir_name
    full_name = os.path.join(dir_name,filename)
    # 确保文件存在
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name

'''
INSERT INTO "public"."dic_blood_desc" VALUES (
'D6686000', NULL, '冰冻单采去白血小板0.5治疗量', '
冰冻单采去白血小板|ACD-A/0.5u', NULL,
'BDDCQBXXB0.5ZLL', 1, 1, 0.5, '125-150ml', '容量：', 'u', 0.5, 0,
'采血时间', 8760, '1年', 0, 1,
'适用于需预防巨细胞病毒感染或因白细胞引起的非溶血性发热输血反应的血小板数量减少或功能障碍的出血患者。',
'-65℃以下', '输注前请检查包装是否完好无损，外观是否正常，融化后尽快输注。', 'ACD-A', '采血者',
'肉眼观察应呈淡黄色云雾状，无纤维蛋白析出、无黄疸、无气泡及重度乳糜出现。', NULL, 1, 0, 0, 0.25, 0);

comment on table "dic_blood_desc" is '血液产品码字典';
comment on column "dic_blood_desc"."id" is '编号';
comment on column "dic_blood_desc"."fullname" is '全称';
comment on column "dic_blood_desc"."subtype" is '血液品种子类型';
comment on column "dic_blood_desc"."type" is '血液品种类型';
comment on column "dic_blood_desc"."capacity" is '容量';
comment on column "dic_blood_desc"."capacitydesc" is '容量描述，用于标签打印。';
comment on column "dic_blood_desc"."capacityprefix" is '容量描述的前缀，用于标签打印。';
comment on column "dic_blood_desc"."unit" is '计量单位';
comment on column "dic_blood_desc"."conversion" is '换算单位';
comment on column "dic_blood_desc"."expirationbeginpoint" is '保质期的计算起始时间。';
comment on column "dic_blood_desc"."expirationhour" is '保质期，按小时为单位。';
comment on column "dic_blood_desc"."expirationdesc" is '保质期描述，用于标签打印。';
comment on column "dic_blood_desc"."collectable" is '可采集，1为可以，0为不可以。';
comment on column "dic_blood_desc"."produceable" is '可制备，1为可以，0为不可以。';
comment on column "dic_blood_desc"."disease" is '适应症';
comment on column "dic_blood_desc"."storecondition" is '储存条件';
comment on column "dic_blood_desc"."useadvise" is '使用注意事项';
comment on column "dic_blood_desc"."anticoagulant" is '保养液';
comment on column "dic_blood_desc"."persononlabel" is '成品标签上所用的工作人员';
comment on column "dic_blood_desc"."appearance" is '外观';
comment on column "dic_blood_desc"."sellable" is '是否可以销售，1为可以，0为不可以';
comment on column "dic_blood_desc"."combinable" is '是否为合并血，1为是，0为不是';
comment on column "dic_blood_desc"."available" is '是否有效，1为有效，0为无效。';


INSERT INTO "public"."dic_blood_desc"(
"id", "fullname", "subtype", "type", "capacity",
"capacitydesc", "capacityprefix", "unit",
"conversion", "expirationbeginpoint",
"expirationhour", "expirationdesc", "collectable",
"produceable", "disease", "storecondition",
"useadvise", "anticoagulant", "persononlabel",
"appearance", "sellable", "combinable", "available")
VALUES ('Z4382', '辐照洗涤红细胞(盐水)(无/300ml/冷藏|去白|照射)',
'201', '02', 1.5, '无/300ml/冷藏|去白|照射', NULL,
'U', 1, NULL, 24, NULL, 0, 0, NULL, '2℃～6℃冷藏',
NULL, NULL, NULL, NULL, NULL, NULL, 1);
'''

def read_raw_datas():
    file_name = 'D:\\Resource\\RFID\\d_blood.json'

    with open(file_name,'r',encoding="utf-8") as f:
        content = f.read()
        blood_dict = json.loads(content)
        blood_list = blood_dict.get('RECORDS')
        return blood_list

def test():
    formatter = 'INSERT INTO dic_blood_desc("id", "fullname", "subtype", "remark", "vendor", "created_at"\
    ) VALUES (SID, TID, FL, RE,'
    rows = read_raw_datas()
    print(rows[1])

test()
