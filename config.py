import json

# sentence_categories = ["术语类", "参考类", "根据类", "属性类", "工序类", "情境类", "要求类"]

data = {"categories":["术语类", "参考类", "根据类", "属性类", "工序类", "情境类", "要求类"],
        
        "regex rules":{"术语类" : r".*[^0-9][^A-Z][a-z]{4,} .*[\u4e00-\u9fa5]+.",
                "参考类" : r".+《.+",
                "根据类" : r".*根据.+",
                "属性类" : r".+[0-9][A-Za-z|°|″|'|％|℃].*",
                "工序类" : r".+前，.+|.+后，.+|.+期间[^；|。].+",
                "情境类" : r".*(当.+时，.+)|(.+时，.+应.+)",
                "要求类" : r"^[^(必须|严禁|应|不应|不得|宜|不宜|可)].+(必须|严禁|应|不应|不得|宜|不宜|可).+"},
        
        "match patterns":
        {"术语类": "",
                
        "参考类":{'ARGM-TMP': '情境描述', 'ARG0': '主体', 'PRED': '符合', 'ARG1': '参考规范',
                'ARGM-LOC': '位置', 'ARGM-MNR': '方式'},
        
        "根据类":{'ARGM-TMP': '情境描述', 'ARG0': '主体', 'PRED': '动作Action', 'ARG1': '对象',
                'ARGM-LOC': '位置', 'ARGM-MNR': '方式'},
        
        "属性类":{'ARGM-TMP': '情境描述', 'ARG0': '主体', 'ARGM-ADV': '否定描述','PRED': '比较描述',
                'ARG1': '数量描述', 'ARGM-LOC': '位置', 'ARGM-MNR': '方式'},

        "工序类":{'ARGM-TMP': '顺序描述', 'ARG0': '主体', 'ARGM-ADV': '否定描述', 'PRED': '动作Action',
                'ARG1': '对象', 'ARGM-LOC': '位置','ARGM-MNR': '方式','PRED-1': '动作Action1', 
                'ARG1-1': '对象1'},
        
        "情境类":{'ARGM-TMP': '情境描述', 'ARG0': '主体', 'ARGM-ADV': '否定描述', 'PRED': '动作Action',
                'ARG1': '对象', 'ARGM-LOC': '位置', 'ARGM-MNR': '方式', 'PRED-1': '动作Action1', 
                'ARG1-1': '对象1'},
        
        "要求类": {'ARGM-TMP': '情境描述', 'ARG0': '主体', 'ARGM-ADV': '否定描述', 'PRED': '动作Action',
                'ARG1': '对象', 'ARGM-LOC': '位置', 'ARGM-MNR': '方式', 'PRED-1': '动作Action1',
                'ARG1-1': '对象1'}
        },
        
        "match patterns config":
        {"术语类": "",
                
        "参考类":{'ARGM-TMP': False, 'ARG0': True, 'PRED': True, 'ARG1': True, 
                'ARGM-LOC': False,'ARGM-MNR': False},
        
        "根据类":{'ARGM-TMP': False, 'ARG0': True, 'ARGM-MNR': True, 'PRED': True, 
                "ARG1": True, 'ARGM-LOC': False},
        
        "属性类":{'ARGM-TMP': False, 'ARG0': True, 'ARGM-ADV': False,'PRED': True,
                'ARG1': True, 'ARGM-LOC': False,'ARGM-MNR': False},

        "工序类":{'ARGM-TMP': True, 'ARG0': True, 'ARGM-ADV' : False, 'PRED': True,
                'ARG1': True, 'ARGM-LOC': False,'ARGM-MNR': False, 'PRED-1': False,
                'ARG1-1': False},
        
        "情境类":{'ARGM-TMP': True, 'ARG0': True, 'ARGM-ADV': False, 'PRED': True,
                'ARG1': True, 'ARGM-LOC': False, 'ARGM-MNR': False, 'PRED-1': False, 
                'ARG1-1': False},
        
        "要求类": {'ARGM-TMP': False, 'ARG0': True, 'ARGM-ADV': False, 'PRED': True,
                'ARG1': True, 'ARGM-LOC': False, 'ARGM-MNR': False, 'PRED-1': False,
                'ARG1-1': False}
        }
}

# 写入 JSON 数据
with open('config.json', 'w', encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)  # Python 字典类型转换为 JSON 对象

js = json.dumps(data, sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False)
print(js)
