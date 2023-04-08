from typing import List, Dict, Tuple


"""功能函数"""


def sentence_preprocess(sentence: str):
    import re
    sentence = sentence.strip()
    pattern = re.compile(r'^\d+(.\d+)*')  # ^([0-9]+)(\.[0-9]+)*
    clause_number = pattern.match(sentence)
    if clause_number is None:
        pass
    else:
        clause_number = clause_number.group()
        # print("clause_number:", clause_number)  # 条款号

        sentence1 = re.sub(pattern, "", sentence)
        sentence = sentence1.strip()
        # print("sentence1:", sentence)

    pattern1 = re.compile(r'[【\(（\[{<](.*?)[】\)）\]}>]', re.S)
    note = pattern1.search(sentence)
    if note is None:
        pass
    else:
        note = note.group()
        # print("note:", note)  # 备注信息

        sentence2 = re.sub(pattern1, '', sentence)
        sentence = sentence2.strip()
        # print("sentence2:", sentence)
    return sentence


def sentence_id_preprocess(sentence: str):
    import re
    sentence = sentence.strip()
    pattern = re.compile(r"^\d+(.\d+)*")  # ^([0-9]+)(\.[0-9]+)*
    _clause_number = pattern.match(sentence)
    if _clause_number is not None:
        _clause_number = _clause_number.group()
        # print("_clause_number:", _clause_number)  # 条款号

        sentence1 = re.sub(pattern, "", sentence)
        sentence = sentence1.strip()
        # print("sentence1:", sentence)

    return sentence, _clause_number


def split_sentence(document: str) -> list:
    """中文分句处理"""
    import re
    sent_list = []
    try:
        document = document.strip()
        document = re.sub('(?P<quotation_mark>([。？！；…](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 单字符断句符
        document = re.sub('(?P<quotation_mark>([。？！；]|…{1,2})[”’"\'])', r'\g<quotation_mark>\n', document)  # 特殊引号
        sent_list_ori = document.splitlines()

        for sent in sent_list_ori:
            sent = sent.strip()
            if not sent:
                continue
            else:
                sent_list.append(sent)
    except:
        sent_list.clear()
        sent_list.append(document)
    return sent_list


def type_analyze(sent: str, sentence_categories: list, classification_rules: list) -> str:
    import re
    
    C = 0
    Flag = True
    while Flag and C < len(classification_rules):
        if re.search(classification_rules[C], sent):
            Clause_Type = sentence_categories[C]
            Flag = False
        else:
            C += 1

    if Flag is True:
        Clause_Type = "未分类"  # 未分类

    # print(Clause_Type)

    return Clause_Type


def shuyu_parse(sentence):
    import re
    sentence = sentence.replace("\n", "")
    sentence, clause_number = sentence_id_preprocess(sentence)
    if re.match(r'.+([a-zA-Z])', sentence):
        jshi = re.sub(r'.+([a-zA-Z])', "", sentence).strip()
        zh_en = re.match(r'.+([a-zA-Z])', sentence).group()
        zh = re.match(r'([\u4e00-\u9fa5]+)', zh_en).group()
        en = re.sub(r'([\u4e00-\u9fa5]+)', "", zh_en).strip()

    print("术语名称:", zh)
    print("英文名称:", en)
    print("术语解释:", jshi)
    
    
"""辅助函数"""


def take_second(elem):
    """获取列表的第三个元素，排序用"""
    return elem[2]


def get_index(lista, x, n):
    # 定义通用的获取某元素在列表中第n次出现的位置下标的函数
    if n <= lista.count(x):
        all_index = [key for key, value in enumerate(lista) if value == x]
        return all_index[n-1]
    else:
        return None


def list_group(lista):
    """列表元素分组, 连续数字段寻找, 保留散点"""
    result_list = []
    for i in range(len(lista)):
        if i < len(lista) - 1:
            if lista[i] + 1 != lista[i + 1]:
                result_list.append([])
    result_list.append([])

    index = 0
    for i in range(len(lista)):
        if i < len(lista) - 1:
            if lista[i] + 1 == lista[i + 1]:
                result_list[index].append(lista[i])
            elif lista[i] != lista[i + 1]:
                result_list[index].append(lista[i])
                index += 1
        elif i == len(lista) - 1:
            result_list[-1].append(lista[-1])

    return result_list


def continusFind(num_list):
    """列表中连续数字段寻找, 不连续的过滤掉"""
    num_list.sort()
    s = 1
    find_list = []
    have_list = []
    while s <= len(num_list)-1:
        if num_list[s]-num_list[s-1] == 1:
            flag = s-1
            while num_list[s]-num_list[s-1] == 1:
                s += 1
            find_list.append(num_list[flag:s])
            have_list += num_list[flag:s]
        else:
            s += 1
    return find_list


def result_process1(srl_dict: dict) -> dict:
    import re
    # 如果后一个的srl标签 = 前一个 ，则合并
    list1 = list(srl_dict.keys())
    list2 = []  # 记录数字

    for i in range(len(srl_dict)):
        if i < len(srl_dict) - 1:
            if re.sub(r"-\d*$", "", list1[i]) == re.sub(r"-\d*$", "", list1[i + 1]):
                list2.append(i)
    if list2:
        list2 = list_group(list2)
        for i in list2:
            i.append(i[-1] + 1)
            srl_dict[list1[i[0]]] = "".join([srl_dict[list1[j]] for j in i])

        for i in list2:
            i.pop(0)  # 删除第一个元素
            for j in i:
                del srl_dict[list1[j]]
    else:
        pass
    return srl_dict


def srls_to_dict(list_optimalsrl: list) -> list:
    from collections import Counter
    K_D = []
    for data in list_optimalsrl:
        data1 = [list(i) for i in data]  # 列表结构

        # 重写标签转为 dict ,否则 覆盖
        keys = [i[1] for i in data]
        c = Counter(keys)
        for k, v in c.items():
            if v >= 2:
                j = 2
                while j <= v:
                    t = get_index(keys, k, j)
                    data1[t][1] = k+"-{}".format(j-1)
                    j += 1

        keys = [i[1] for i in data1]
        values = [i[0] for i in data1]
        d = {k: v for k, v in zip(keys, values)}
        
        d = result_process1(d)  # srl_dict 相邻键（如果对应相同srl角色）键值合并
        K_D.append(d)

    return K_D


def analyze_spo(data):
    """主宾关系分析，标签重构"""
    # TODO: data 可先去掉副词
    keys = [i[1] for i in data]
    
    subject = False
    object = False
    subject_id = None
    object_id = []
    for m, n in enumerate(keys):
        if m < len(keys)-1:
            if keys[m+1] == "PRED":
                if subject is False and (n in ["ARG0", "ARG1", "ARG2", 'ARGM-TPC']):
                    if m-1 >= 0 and (keys[m-1] != "PRED"):
                        # print("subject:", data[m]) # subject在"PRED"前，且不在"PRED"后
                        subject = True
                        subject_id = m
                        continue
                    
                    elif m == 0 and (keys[m+1] == "PRED"):
                        # print("subject:", data[m]) # subject为首个SRL角色
                        subject = True
                        subject_id = m
                        continue
                    
                if m-1 >= 0 and keys[m-1] == "PRED" and (n in ["ARG0", "ARG1", "ARG2"]):
                    # print("object:", data[m]) # object在两个"PRED"之间
                    object = True
                    object_id.append(m)
                    continue
                
            elif keys[m-1] == "PRED" and (n in ["ARG0", "ARG1", "ARG2"]):
                # print("object:", data[m]) # object在"PRED"后
                object = True
                object_id.append(m)
                continue
            
        else:
            if keys[m-1] == "PRED" and (n in ["ARG0", "ARG1", "ARG2"]):
                #print("object:", data[m]) # object在"PRED"后
                object = True
                object_id.append(m)
                
    if subject is True:
        m = subject_id
        data[m][1] = "ARG0"
    if object is True:
        for i in object_id:
            data[i][1] = "ARG1"
    return data


def result_process1_new(df):
    import re
    """冲突处理"""

    def process():
        """srl_dict 相邻键 键值合并（如果相邻键对应相同srl角色）"""
        list1 = df.columns
        for i in range(len(list1)):
            if i < len(list1) - 1:
                if re.sub(r"-\d*$", "", list1[i]) == re.sub(r"-\d*$", "", list1[i + 1]):
                    df[list1[i]] = df[list1[i]].astype(str)
                    df[list1[i + 1]] = df[list1[i + 1]].astype(str)
                    df[list1[i]] = df[[list1[i], list1[i + 1]]].agg(''.join, axis=1)
                    df.drop(columns=list1[i + 1],inplace =True)
    while 1:
        T = len(df.columns)
        process()
        if len(df.columns) == T:
            break
    
    # 只有 ARG0 + PRED  替换为 ARG0 + ARG1
    list1 = df.columns
    if list1[-1]== "PRED" and ('ARG1' not in list1) and (len(list1)==2):
        df.rename(columns={'PRED':'ARG1'}, inplace=True)
        # df["PRED"] = "Should" # 新增列
        df.insert(1, 'PRED', "Should")
        # print("conflict5")
        
    return df


def one_srl_to_df(one_srl: List[Tuple[str]]):
    from collections import Counter
    import pandas as pd
    
    data = [list(i) for i in one_srl]  # 列表结构
    data = analyze_spo(data)
    
    # 重写标签, 否则转为dict时, 键覆盖
    keys = [i[1] for i in one_srl]
    c = Counter(keys)
    for k, v in c.items():
        if v >= 2:
            j = 2
            while j <= v:
                t = get_index(keys, k, j)
                data[t][1] = k + "-{}".format(j - 1)
                j += 1

    keys = [i[1] for i in data]
    values = [i[0] for i in data]
    d = {k: v for k, v in zip(keys, values)}  # srl_dict
    
    D = pd.DataFrame(d, index=[0])
    D = result_process1_new(D)  # 冲突处理

    return D


def pattern_match(Clause_Type: str, one_srl: List[Tuple[str]], sentence_categories: list, match_patterns: list) -> list:
    import pandas as pd
    import json
    import numpy as np
    D = one_srl_to_df(one_srl)
    df = pd.DataFrame(D)
    
    df1 = df.reindex(['ARGM-TMP','ARG0','ARGM-ADV','PRED','ARG1','PRED-1','ARG1-1','ARGM-LOC','ARGM-MNR'], axis=1) # 重置索引

    def function1(a):
        if a in ["不应", "不该", "不能", "不宜", "不许", "不可", "不得", "不", "不必", "不需", "无需"]:
            return a
        else:
            return np.nan
    
    for i in range(len(sentence_categories)):
        if Clause_Type == sentence_categories[i]:
            df1.dropna(thresh=2, inplace=True)
            
            if Clause_Type == "参考类":
                df1 = df1[(df1["PRED"] == "符合") | (df1["PRED"] == "参照")]
                # df1 = df1[df1["PRED"].isin(["符合", "参照"])]
                
            elif Clause_Type == "属性类":
                if 'ARGM-ADV' in df1.columns:
                    df1 = df1[df1['ARGM-ADV'].isnull() | (df1['ARGM-ADV'].astype(str).str.contains("不"))]
                    # df1 = df1[df1['ARGM-ADV'].isin(["不应", "不该", "不能", "不宜", "不许", "不可", "不得", "不", np.nan])]                
                df1 = df1[df1['PRED'].isin(["少于", "小于", "低于", "超过", "大于", "高于", "达到"])]
                
            df1.rename(columns=match_patterns[i], inplace=True)
            
            if '否定描述' in df1.columns:
                if  df1['否定描述'].isnull().all():
                    pass
                else:
                    df1['否定描述'] = df1.apply(lambda x: function1(x["否定描述"]), axis=1)
            break

    # 重置索引, 方便后续DataFrame的concat纵向堆叠操作
    df1 = df1.reindex(['情境描述','顺序描述','主体','参照规范','否定描述','比较描述','数量描述','动作Action','对象','动作Action1','对象1','位置','方式'], axis=1)
    
    # 展示
    df2 = df1.dropna(how='all', axis=1, inplace=False)  # 删除空列，便于展示
    result = df2.to_json(orient ='records',force_ascii=False)  # json
    parsed = json.loads(result)  # json -> python
    js = json.dumps(parsed, indent=4, sort_keys=False, ensure_ascii=False)  # python -> json 
    print(js)  # type: str
    
    return df1
