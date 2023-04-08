import copy

'''附加函数'''

def tok_custom_dict(*_dict_file_name, _user_set=None):
    """读取自定义词典，生成set形式
    load_userdict"""

    if _dict_file_name is None:
        return None
    else:
        _user_dict = []
        for file in _dict_file_name:
            with open(file, "r", encoding='utf-8') as f:
                words = f.readlines()
                tok_dict_sett = []
                for word in words:
                    word = word.strip("\n")
                    tok_dict_sett.append(word)
            _user_dict.extend(tok_dict_sett)
            _user_set = set(_user_dict)
        return _user_set


def take_second(elem):
    """获取列表的第三个元素，排序用"""
    return elem[2]


def take_coordinates(list_co):
    """获取_srl_formatlist的定位坐标，后两位元素"""
    list_coordinates = []
    for item in list_co:
        list_coordinates.append(item[2:4])
    return list_coordinates


def take_element(list_coo, coordinates):
    """输入坐标，得出_srl_formatlist对应的最优元素"""
    for item in list_coo:
        if coordinates == item[2:]:
            return item
        elif coordinates[-2] >= item[-2] and coordinates[-1] <= item[-1]:
            return item


def process_w(w_list):
    """返回  "w"  pos标签的列表键值 id
    pku 词性标注标准下标点符号的标签为 "w" ; CTB 标准下标点符号的标签为  "PU" """

    list_filter = ["，", "。", "（", "）", "；", "："]  # 适合中文文本符号
    list_w = [sep for sep, element in enumerate(w_list) if element[1] in ["w", "PU"] and element[0] in list_filter]
    if w_list[-1][-1] in ["w", "PU"]:
        pass
    else:
        # 末尾没标点符号
        list_w.append(len(w_list))
    
    return list_w


def process_ww(ww_list):
    """根据pos标签的位置，返回区间列表 return list_ww"""
    list_ww = []
    if len(ww_list) >= 2:
        list_ww.append((0, ww_list[0]))

        for i, j in zip(ww_list, range(len(ww_list))):
            if j + 1 < len(ww_list):
                list_ww.append((i + 1, ww_list[j + 1]))
            else:
                pass
        # print("list_ww:", list_ww)
    elif len(ww_list) == 1:
        list_ww.append((0, ww_list[0]))
    else:
        pass

    return list_ww


def remove_duplicates(srls):
    """组内和组间去重"""
    duplicated_srls = []
    for i in srls:
        i = list(set(i))  # 组内去重
        i.sort(key=take_second)  # 排序
        if i not in duplicated_srls:
            duplicated_srls.append(i)  # 组间去重

    '''组间包含情况, 去除被包含的'''
    if len(duplicated_srls) <= 1:
        return duplicated_srls
    else:
        # x.issuperset(y)  # 判断集合 y 的所有元素是否都包含在集合 x 中

        list_srl_remove = []  # 将被剔除的srl组
        for i in duplicated_srls:
            for j in duplicated_srls:
                if i == j:
                    pass
                else:
                    if set(i).issuperset(set(j)):
                        if j not in list_srl_remove:
                            list_srl_remove.append(j)  # 删除j

        super_duplicated_srls = []
        for i in duplicated_srls:
            if i not in list_srl_remove and i not in super_duplicated_srls:
                super_duplicated_srls.append(i)

        return super_duplicated_srls


'''NLP功能函数'''


def process_1(doc_srl):
    """处理1：词语包含问题，，，得到list_srls_great111"""

    '''去重得到有效srl角色列表, list1_srl_formatlist'''
    list1_srl_formatlist = []  # 所有不同srl 标记的字符, 去除掉无srl信息的词
    list1_srl_num = []  # 去重后 各srl角色定位坐标列表

    for i in doc_srl:
        for j in i:
            # print([i]) # 每次srl结果
            # print()
            if j[2:4] not in list1_srl_num:
                list1_srl_num.append(j[2:4])  # 只取后两个参数，作为srl角色定位坐标

    for i in doc_srl:
        for j in i:
            if j[2:] in list1_srl_num:
                # print([j][0:2])
                if j[2:] not in take_coordinates(list1_srl_formatlist):
                    list1_srl_formatlist.append(j)  # 同一个词有多个srl标签，只添加第一次

    # print("list1_srl_formatlist:", list1_srl_formatlist) # 未排序
    # print()
    # print("list1_srl_num:", list1_srl_num)  # 未排序
    # print()

    '''剔除被词语包含的srl元素'''
    list2_srl_remove = []  # 被包含的srl词语列表，需要剔除
    for i in list1_srl_formatlist:
        for j in list1_srl_formatlist:
            if i[-2] == j[-2] and i[-1] == j[-1]:
                pass

            elif i[-2] >= j[-2] and i[-1] <= j[-1]:  # i被j包含
                if i not in list2_srl_remove:
                    list2_srl_remove.append(i)

    # print("list2_srl_remove:", list2_srl_remove)
    # print()

    '''去包含（重叠）后，最优srl角色列表、定位坐标'''
    list2_srl_formatlist = []
    for i in list1_srl_formatlist:
        if i not in list2_srl_remove:
            list2_srl_formatlist.append(i)

    # print("list2_srl_formatlist:", list2_srl_formatlist)
    # print()

    # 坐标可使用take_coordinates() 函数而来
    list2_srl_num = take_coordinates(list2_srl_formatlist)

    if list1_srl_formatlist != list2_srl_formatlist:
        '''根据定位符替换掉被各srl组中被包含的词语'''
        list1_srls_prepare = copy.deepcopy(doc_srl)  # 对list1_srls_prepare进行不断替换

        for i in list1_srls_prepare:
            for j, m in zip(i, range(len(i))):
                i[m] = take_element(list2_srl_formatlist, j[2:])  # 输入列表和坐标，取出元素,进行更换

        # print("list1_srls_prepare:", list1_srls_prepare)
        # print()
    else:
        list1_srls_prepare = copy.deepcopy(doc_srl)

    '''对 list1_srls_prepare进行组内和组间去重，以及处理组间包含情况,得到 list_srls_great111'''
    list_srls_great111 = remove_duplicates(list1_srls_prepare)

    # print("list_srls_great111:", list_srls_great111)
    # print()

    return list2_srl_formatlist, list_srls_great111, list1_srl_num, list2_srl_num


def process_2(sentence_tok, sentence_pos, list2_srl_formatlist, list_srls_great111):
    """处理2：符号之间srl合并问题，，，得到------>>>第二轮的最优srl结果 list_srls_great222"""
    """两个逗号之间的srl结果应该放在一起    根据定位符将逗号之间的结果添加进每组srl中"""

    """获取标点符号punctuation位置，确定分类区间"""
    keys = sentence_tok
    values = sentence_pos
    zip1 = zip(keys, values)
    list_pku = list(zip1)
    # print("list_pku:",list_pku)
    # print()

    list_w = process_w(list_pku)
    # print("list_w:",list_w)
    # print()

    list_ww = process_ww(list_w)
    # print("list_ww:", list_ww)
    # print()
    
    if len(list_srls_great111) == 1:
        list_srls_great222 = list_srls_great111
        
    else:
        dict_w = {}
        '''按标点符号的位置，对srl角色进行分类'''
        # {0: [()], 1: [(), ()], 2: [()], 3: [(), (), ()]}

        for item1, item2 in zip(list_ww, range(len(list_ww))):
            for item3 in list2_srl_formatlist:
                if int(item3[-2]) > int(item1[1]):
                    dict_w.setdefault(item2, [])  # 键值为空
                if int(item3[-2]) >= int(item1[0]) and int(item3[-1]) <= int(item1[1]):
                    dict_w.setdefault(item2, []).append(item3)
                else:
                    pass
        # print("dict_w:", dict_w)
        # print()

        '''对每组srl结果进行扩充'''

        list2_srls_prepare = copy.deepcopy(list_srls_great111)
        # list2_srls_prepare发生了变化

        for i, m in zip(range(len(list2_srls_prepare)), list2_srls_prepare):
            for j in range(len(dict_w)):
                d1 = [True for c in dict_w[j] if c in list2_srls_prepare[i]]
                # 某组SRE是否在当前SRL组中 --- 布尔列表
                d2 = [False for c in dict_w[j] if c not in list2_srls_prepare[i]]
                # 某组的SRE是否不在当前SRL组中 --- 布尔列表
                if d1 and d2 and len(d1) != 1:
                    if len(list_ww) !=1 and len(dict_w[0]) != 1 and j == 0:
                        # 一个句子中有多个短句，且第一组包含多个SRE时; 不考虑第一组（句首到第一个符号）
                        pass
                    else:
                        # 语义传递 != 1 时, 添加SRE, 否则不变; 即不考虑本组SRE只有一个在其他组的情况
                        for n in dict_w[j]:
                            if n not in m:
                                m.append(n)

        '''对 list2_srls_prepare进行组内和组间去重，以及处理组间包含情况，得到 list_srls_great222'''
        list_srls_great222 = remove_duplicates(list2_srls_prepare)
    return list_srls_great222


def process_3(list_srls_great222, list2_srl_formatlist, semantic_delivery=False):
    """处理3：移除无效srl组，，，得到------>>>第三轮的最优srl结果 list_srls_optimal"""
    list3_srls_prepare = copy.deepcopy(list_srls_great222)

    first_sre = list2_srl_formatlist[0]  # list2_srl_formatlist为最优SRE序列
    list_srls_optimal = []  # 最优结果
    
    for i in list3_srls_prepare:
        count = 0
        for j in range(len(i)):
            count += len(i[j][0])
            
        if len(i) > 2 and count > 6:  # 包含2个以上srl元素以及字数总和大于6 的srl组 --- 留下
            if i not in list_srls_optimal:
                list_srls_optimal.append(i)
                
        elif len(i) == 2:  # 包含2个srl元素的srl组 ---- 判断保留
            if i[0][1] in ["ARG0", "ARG1", "ARG2", "ARGM-TPC", "ARGM-TMP"] and i[1][1] == "PRED":
                if i not in list_srls_optimal:
                    list_srls_optimal.append(i)
        else:
            if semantic_delivery:
                if first_sre not in i:
                    i.insert(0, first_sre)  # 被剔除的SRL, 继承前一个主语性的SRE, 增加召回率
                    count = 0
                    for j in range(len(i)):
                        count += len(i[j][0])
                    if len(i) > 2 and count > 6:
                        if i not in list_srls_optimal:
                            list_srls_optimal.append(i)
                            
    return list_srls_optimal
