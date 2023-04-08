import hanlp
from hanlp_common.document import Document
from config.process_new import *
from config.help_functions_new import *
import copy
from config.hanlp_conf import model_configuration


def hanlp_progress(sent):
    """
    原始 HanLP 的 SRL 处理结果
    处理方式：直接传入句子基于 HanLP 多任务联合处理模型进行 SRL 处理; 默认细粒度分词, 默认 pos/pku 词性标注标准;
    """
    sent = sentence_preprocess(sent)  # 句子预处理函数
    doc = HanLP(sent)
    print(sent)
    print()
    # doc.pretty_print()

    """将SRL结果分级输出"""
    print("Original_srls_result:")
    print()

    for i in doc["srl"]:
        print(i)
        # for j in i:
        #     print(j[0:2])
    print()


def hanlp_optimize_progress(sent):
    """句子级优化处理：SRL 后优化处理
    :param sent
    """
    sent = sentence_preprocess(sent)  # 句子预处理函数
    doc = HanLP(sent)
    sentence_tok = doc["tok/fine"]
    sentence_pos = doc["pos/pku"]
    print(sent)
    print(sentence_tok)
    print(sentence_pos)
    print()
    # doc.pretty_print()
    print("Original_srls_result:")
    print(doc["srl"])
    print()
    
    for i in doc["srl"]:
        print(i)
        # for j in i:
        #     print(j[0:2])
    print()

    if len(doc['srl']) == 0:
        print("无srl结果")
        pass

    elif len(doc['srl']) == 1:
        one_srl = doc['srl'][0]
        if len(one_srl) > 2:
            print("无需srl后优化处理")
            list_srls_optimal = doc['srl']
        
        elif len(one_srl) == 2:
            if one_srl[0][1] in ["ARG0", "ARG1", "ARG2", "ARGM-TPC", "ARGM-TMP"] and one_srl[1][1] == "PRED":
                print("无需srl后优化处理")
                list_srls_optimal = doc['srl']
            else:
                print("有srl, 剔除")
        else:
            print("有srl, 剔除")
        
    else:
        '''srl优化处理'''
        doc_srl = doc['srl']

        """处理1:词语包含问题，，，得到list_srls_great111"""

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

        print("list1_srl_formatlist:", list1_srl_formatlist)  # 未排序
        print()
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

        print("list2_srl_formatlist:", list2_srl_formatlist)
        print()

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

        print("list_srls_great111:", list_srls_great111)
        print()


        """处理2：符号之间srl合并问题，，，得到第二轮的最优srl结果 list_srls_great222"""
        """两个逗号之间的srl结果应该放在一起，根据定位符将逗号之间的结果添加进每组srl中"""
        if merge_between_symbols is False:
            list_srls_great222 = list_srls_great111
        else:
            """获取标点符号punctuation位置，确定分类区间"""
            keys = sentence_tok
            values = sentence_pos
            zip1 = zip(keys, values)
            list_pku = list(zip1)
            # print("list_pku:",list_pku)
            # print()
            
            list_w = process_w(list_pku)
            print("list_w:",list_w)
            print()

            list_ww = process_ww(list_w)
            print("list_ww:", list_ww)
            print()
            
            # end_punctuation =  True if list_pku[-1][-1] in ["w", "PU"] else False
            
            # if ((end_punctuation is True and len(list_ww) == 1)
            #     or (end_punctuation is False and len(list_ww) == 0) 
            #     or len(list_srls_great111) == 1):
            
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

                print("dict_w:", dict_w)
                print()

                '''对每组srl结果进行扩充'''

                list2_srls_prepare = copy.deepcopy(list_srls_great111)
                # list2_srls_prepare发生了变化

                for i, m in zip(range(len(list2_srls_prepare)), list2_srls_prepare):
                    for j in range(len(dict_w)):
                        d1 = [True for c in dict_w[j] if c in list2_srls_prepare[i]]
                        d2 = [False for c in dict_w[j] if c not in list2_srls_prepare[i]]
                        if d1:
                            if d2:
                                if len(d1) != 1:
                                    if len(list_ww) !=1 and len(dict_w[0]) != 1 and j == 0:
                                        # 一个句子中有多个短句，第一组包含多个SRE时; 不考虑第一组（句首到第一个符号）
                                        pass
                                    else:
                                        # 语义传递 != 1 时, 添加SRE, 否则不变; 即不考虑本组SRE只有一个在其他组的情况
                                        for n in dict_w[j]:
                                            if n not in m:
                                                m.append(n)

                '''对 list2_srls_prepare进行组内和组间去重，以及处理组间包含情况，得到 list_srls_great222'''
                list_srls_great222 = remove_duplicates(list2_srls_prepare)

            print("list_srls_great222:", list_srls_great222)
            print()
            
            
        """处理3：移除无效srl组，，，得到第三轮的最优srl结果 list_srls_optimal"""
        if remove_invalid_symbols is False:
            list_srls_optimal = list_srls_great222
        else:
            list_srls_great333 = copy.deepcopy(list_srls_great222)

            first_sre = list2_srl_formatlist[0]
            list_srls_optimal = []  # 最优结果

            for i in list_srls_great333:
                count = 0
                for j in range(len(i)):
                    count += len(i[j][0])
                # print(count)
                if len(i) > 2 and count > 6:  # 每组srl  包含2个以上srl 元素以及字数总和大于6 的srl组留下
                    if i not in list_srls_optimal:
                        list_srls_optimal.append(i)
                elif len(i) == 2:
                    if i[0][1] in ["ARG0", "ARG1", "ARG2", "ARGM-TPC", "ARGM-TMP"] and i[1][1] == "PRED":
                        if i not in list_srls_optimal:
                            list_srls_optimal.append(i)
                else:
                    if semantic_delivery:
                        if first_sre not in i:
                            i.insert(0, first_sre)  # 被剔除的SRL继承，首个最优SRE，增加召回率
                            count = 0
                            for j in range(len(i)):
                                count += len(i[j][0])
                            if len(i) > 2 and count > 6:
                                if i not in list_srls_optimal:
                                    list_srls_optimal.append(i)

        if len(list_srls_optimal) == 0:
            print("被剔除:")
            print(list_srls_great333)

        else:
            '''将最优结果分级输出'''
            print("list_srls_optimal:", list_srls_optimal)  # 最终结果
            print()

            for i in list_srls_optimal:
                i.sort(key=take_second)  # 排序
                print(i)
            #     for j in i:
            #         print(j[0:2])  # 只取前两个参数，即srl角色和标签，，忽略定位值
            #     print()
            print()

    """优化后可视化"""
    sentence_nlp = {"tok": sentence_tok, "pos": sentence_pos, "srl": list_srls_optimal}
    doc = Document(sentence_nlp)
    # print(sentence_tok)
    # print(list_srls_optimal)
    doc.pretty_print()


'''自定义模型配置，得到HanLP'''
# user_dictionary_path = "dict.txt"  # 自定义词典
# user_dict_set = {}

user_dictionary_path = None
user_dict_set = {'不应', '并应', '不得', '不宜', '盾构', '滚转角', '工作井', '注浆', '注浆口', '注浆量', '一般项目',
                    '控制点', '水准测量', '且应', '测量较差', '放样', '相适应', '验算', '可调', '可配置', '测设', '也可',
                    '持证上岗', '漏涂', '漏浆', '应对', '尚应', '套箍', '遇水膨胀防水材料',
                    '注浆孔', "排土量", "始发", "复测", "迁站", "压面", "施焊", "壁后注浆", "管片", "混凝土"}

HanLP = model_configuration(_way="U", _tok_granularity='tok/fine', _pos='pos/pku',
                            user_dict_paths=user_dictionary_path, user_dynamic_dictionary=user_dict_set)

'''联合处理模型'''
# HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH)
HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)

merge_between_symbols = True  # False
remove_invalid_symbols = True  # False
semantic_delivery = False # 语义传递

if __name__ == '__main__':
    
    '''测试一个句子'''
    
    # sentence0 = "当存在可燃性或有害气体时，应使用专用仪器进行检测，并应加强通风措施，气体浓度应控制在安全允许范围内。"
    # sentence0 = "管片贮存场地应坚实平整。"
    sentence0 = "泥浆压力与开挖面的水土压力应保持平衡，排出渣土量与开挖渣土量应保持平衡，并应根据掘进状况进行调整和控制"
    sentence0 = "根据建(构)筑物基础与结构的类型、现状和沉降控制值等，可采取加固、隔离或托换等措施；"
    # "焊接前应对焊接处进行检查，不应有水锈、油渍，焊接后不应有焊接缺陷；"
    # "同一钢筋骨架不得使用多于2根带有接头的纵向受力钢筋，且不得相邻布置；"
    # "组装后，应先进行各系统的空载调试，然后应进行整机空载调试。"
    # "特殊工种应持证上岗。"
    # 泥水循环系统应根据地质和施工条件等确定，并应具备掘进模式和旁通模式，流量应连续可调，可配置渣石处理装置。
    # 盾构法隧道施工应具有施工管理体系，应建立质量控制和检验制度，并应采取安全和环境保护措施。
    # hanlp_progress(sentence0)  # 原始SRL结果
    hanlp_optimize_progress(sentence0)  # 优化后结果
    
    # '''句子列表'''
    # Sentences_List = ['钢管片的螺栓孔应畅通，内圆面应平整；',
    #                   '管片贮存场地应坚实平整。',
    #                   '掘进施工应控制排土量、盾构姿态和地层变形。',
    #                   '管片严重开裂或严重错台；',
    #                   '对掘进施工影响范围内的岩溶和洞穴，应采取注浆等措施处理。',
    #                   '发生故障或运转不稳定；',
    #                   '应利用隧道内测量控制点采用极坐标法放样隧道中心线和盾构基座的位置、方向，应利用水准测量方法测设隧道高程控制线以及基座坡度，坐标和高程放样中误差为±5mm；',
    #                   '隧道结构监测初始值宜在管片壁后注浆凝固后12h内测量。']
    #
    # for sentence0 in Sentences_List:
    #     hanlp_progress(sentence0)  # 原始SRL结果
    #     hanlp_optimize_progress(sentence0)  # 优化后结果
