from config.process_new import *
from config.help_functions_new import *
from config.hanlp_conf import HanLP
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os
import sys

# 输出重定向, 可用于生成评估文件
# sys.stdout = open('IE记录1.log', mode='w', encoding='utf-8')


def hanlp_progress(sentence):
    """
    原始 HanLP 的 SRL 处理结果
    处理方式：直接传入句子基于 HanLP 多任务联合处理模型进行 SRL 处理; 默认细粒度分词, 默认 pos/pku 词性标注标准;
    """
    doc = HanLP(sentence)
    print(sentence)
    sentence_pos_show = HanLP(sentence, skip_tasks="srl")
    sentence_pos_show.pretty_print()
    print()
    doc.pretty_print()

    """将SRL结果分级输出"""
    print("Original_srls_result:")
    print()

    for i in doc["srl"]:
        print(i)
        # for j in i:
        #     print(j[0:2])
    print()

    return


def hanlp_optimize_progress(sentence, merge_between_symbols=True):
    """句子级优化处理：SRL 后优化处理
    :param sentence
    :param merge_between_symbols: 是否进行处理2,默认进行
    :return sentence, doc['srl'], list_srls_optimal
    """
    doc = HanLP(sentence)

    def doc_normalization():
        """doc结果归一化"""
        nonlocal doc
        t = p = None
        for _i in doc.keys():
            if "tok" in _i:
                t = _i
            if "pos" in _i:
                p = _i
        doc["tok"] = doc.pop(t)
        doc["pos"] = doc.pop(p)

    doc_normalization()  # doc结果归一化
    sentence_tok = doc["tok"]
    sentence_pos = doc["pos"]
    print("@开始")
    print(sentence)
    # sentence_pos_show = HanLP(sentence, skip_tasks="srl")
    # sentence_pos_show.pretty_print()
    # doc.pretty_print()

    if len(doc['srl']) == 0:
        print("无srl结果")
        print()
        pass

    elif len(doc['srl']) == 1:
        print("无需优化处理")
        print()
        if len(doc['srl'][0]) < 2:  # 原<=2，对于单个句子 = 2时也不剔除
            print("直接剔除")
            print()
        else:
            for i in doc['srl']:
                print(i)
                # for j in i:
                #     print(j[0:2])
            print()

    else:
        '''srl优化处理'''
        doc_srl = doc['srl']

        """处理1：词语包含问题，，，得到------>>>list_srls_great111"""
        list2_srl_formatlist, list_srls_great111, list1_srl_num, list2_srl_num = process_1(
            doc_srl)

        """处理2：符号之间srl合并问题，，，得到------>>>第二轮的最优srl结果 list_srls_great222"""
        if merge_between_symbols:
            list_srls_great222 = process_2(
                sentence_tok, sentence_pos, list2_srl_formatlist, list_srls_great111)
        else:
            list_srls_great222 = list_srls_great111

        """处理3：移除无效srl组，，，得到------>>>第三轮的最优srl结果 list_srls_optimal"""
        list_srls_optimal = process_3(
            list_srls_great222, list2_srl_formatlist, semantic_delivery=False)

        """将最优结果分级输出"""
        if list_srls_optimal:
            print("Optimal_srls_result:")
            print()

            for i in list_srls_optimal:
                i.sort(key=take_second)  # 排序
                print(i)
                # for j in i:
                #     print(j[0:2])  # 只取前两个参数，即srl角色和标签，，忽略定位值
            print()
        else:
            print("被最终剔除")
            print(list_srls_great222)
            print()


def file_process(_file_name):
    with open(_file_name, "r", encoding='utf-8') as f:
        with tqdm(f.readlines(), desc=f"{_file_name} @processing", position=0) as t:
            for sent in t:
                sent = sentence_preprocess(sent)  # 句子预处理函数
                sents = split_sentence(sent)  # 分句
                for _sent in sents:
                    hanlp_optimize_progress(_sent)


class ReadFile:
    """
    读取文件进行Hanlp后优化处理;
    统计功能
    """

    def __init__(self):
        """统计功能参数"""
        self.List_Evaluation_Indicator_1 = []
        self.List_Evaluation_Indicator_2 = []

        self.list_no_process = []  # 无需处理
        self.list_no_srl = []  # 无结果
        self.list_srl_process_remove = []  # 有结果，但被剔除
        self.list_srls_process_optimal = []  # 优化处理的句子

        self.list_srls_process_optimal_num = 0

        self.KEs_num = 0
        self.K_Ds = []
        self.KE_num = 0
        self.sent_num = 0

        self.double_KT = []  # 二元组


    def hanlp_optimize_progress(self, sent, merge_between_symbols=True, remove_invalid_symbols=True):
        """句子级优化处理
        :param sent
        :param merge_between_symbols: 是否进行处理2,默认不进行
        :return sentence, doc['srl'], list_srls_optimal
        """
        doc = HanLP(sent)

        def doc_normalization():
            """doc结果归一化"""
            nonlocal doc
            t = p = None
            for k in doc.keys():
                if "tok" in k:
                    t = k
                if "pos" in k:
                    p = k
            doc["tok"] = doc.pop(t)
            doc["pos"] = doc.pop(p)

        doc_normalization()  # doc结果归一化
        sentence_tok = doc["tok"]
        sentence_pos = doc["pos"]

        if len(doc['srl']) == 0:
            self.list_no_srl.append(sent)
            print("无结果")
            return sent, False, False

        elif len(doc['srl']) == 1:
            '''无需srl后优化处理'''
            # evaluation_indicator_1 = 1
            # evaluation_indicator_2 = 1

            # self.List_Evaluation_Indicator_1.append(evaluation_indicator_1)
            # self.List_Evaluation_Indicator_2.append(evaluation_indicator_2)
            
            one_srl = doc['srl'][0]
            
            if len(one_srl) > 2:
                self.list_no_process.append(sent)
                print("无需srl后优化处理")
                return sent, doc['srl'], doc['srl']
            
            elif len(one_srl) == 2:
                if one_srl[0][1] in ["ARG0", "ARG1", "ARG2", "ARGM-TPC", "ARGM-TMP"] and one_srl[1][1] == "PRED":
                    self.list_no_process.append(sent)
                    print("无需srl后优化处理")
                    return sent, doc['srl'], doc['srl']
                
                else:
                    self.list_srl_process_remove.append(sent)
                    print("有srl, 剔除")
                    return sent, doc['srl'], False
                
            else:
                self.list_srl_process_remove.append(sent)
                print("有srl, 剔除")
                return sent, doc['srl'], False
            
        else:
            '''srl优化处理'''
            doc_srl = doc['srl']
            
            """处理1：词语包含问题，，，得到list4_change"""
            list2_srl_formatlist, list_srls_great111, list1_srl_num, list2_srl_num = process_1(
                doc_srl)

            """处理2：符号之间srl合并问题，，，得到------>>>第二轮的最优srl结果 list_srls_great222"""
            if len(list_srls_great111) == 1 or merge_between_symbols is False:
                list_srls_great222 = list_srls_great111
                
            if merge_between_symbols:
                list_srls_great222 = process_2(
                    sentence_tok, sentence_pos, list2_srl_formatlist, list_srls_great111)
                
            """处理3：移除无效srl组，，，得到------>>>第三轮的最优srl结果 list_srls_optimal"""
            if remove_invalid_symbols:
                list_srls_optimal = process_3(
                    list_srls_great222, list2_srl_formatlist, semantic_delivery=False)
            else:
                list_srls_optimal = list_srls_great222
                
            """流程评估"""
            if len(list_srls_optimal) == 0:
                self.list_srl_process_remove.append(sent)
                print("后续剔除")
                # evaluation_indicator_1 = 0
                # evaluation_indicator_2 = 0

                # self.List_Evaluation_Indicator_1.append(evaluation_indicator_1)
                # self.List_Evaluation_Indicator_2.append(evaluation_indicator_2)
                return sent, doc['srl'], False
            
            else:
                self.list_srls_process_optimal_num += 1

                evaluation_indicator_1 = len(
                    list_srls_optimal) / len(doc["srl"])
                evaluation_indicator_2 = len(
                    list2_srl_num) / len(list1_srl_num)

                self.List_Evaluation_Indicator_1.append(evaluation_indicator_1)
                self.List_Evaluation_Indicator_2.append(evaluation_indicator_2)
                    
                return sent, doc['srl'], list_srls_optimal

    '''统计功能函数'''

    def result_statistics(self):
        """统计结果输出"""
        # print(List_Evaluation_Indicator_1)
        # print(List_Evaluation_Indicator_2)

        a = len(self.list_no_process)
        b = len(self.list_no_srl)
        c = len(self.list_srl_process_remove)
        d = self.list_srls_process_optimal_num

        print("无需处理句子个数为:", a)
        print("无结果句子个数为:", b)
        print("有srl结果，但被剔除句子个数为:", c)
        print("优化处理的句子个数为:", d)

        print()
        print("无需处理:", self.list_no_process)
        print("无结果:", self.list_no_srl)
        print("有srl结果，但被剔除:", self.list_srl_process_remove)
        print()
        print("知识元组个数:", self.KEs_num)  # 知识元组个数
        print("知识元个数:", self.KE_num)  # 知识元个数
        print("句子个数:", self.sent_num)  # 句子个数


    def result_statistics_draw(self):
        """
        说明:
        当Indicator1等于1且 NSRLs=1时，说明当前条款的原始SRL结果无需处理即为最优；
        当Indicator2等于1时，说明条文不存在词语包含问题；当两个指标纵坐标的值越小时，说明对当前条款的SRL结果优化程度越高；
        当纵坐标为0时，说明SRL结果被最终剔除。
        """
        config = {
            "font.family":'serif',
            "font.size": 12, # 小四
            "mathtext.fontset":'stix',
            "font.serif": ['Times New Roman'], # SimSun 宋体
            "axes.unicode_minus": False, # 用来正常显示正负号
            "xtick.direction" : "in", # 刻度 in内测，默认out外侧
            "ytick.direction" : "in"
        }
        
        rcParams.update(config)
        
        a = np.array(self.List_Evaluation_Indicator_1)
        b = np.array(self.List_Evaluation_Indicator_2)

        print(np.mean(a))
        print(np.mean(b))

        y1 = self.List_Evaluation_Indicator_1
        y2 = self.List_Evaluation_Indicator_2
        x = np.arange(0, len(y1), 1)

        # 绘制坐标标题
        plt.title("Evaluation_Statistics")

        # 绘制x、y轴备注
        plt.xlabel("Clause", loc="right")   # "条文"
        plt.ylabel("Evaluation_Indicator")  # "评估指标", loc="top"

        # 绘制数据
        plt.plot(x, y1, color='teal', linestyle='-',
                        linewidth=1, label='Indicator1')
        plt.plot(x, y2, color='orange', linestyle='dashdot',
                        linewidth=1, label='Indicator2')

        # 绘制图例
        plt.legend(loc=1) # (fig1[0], fig2[0]), ['Indicator1', 'Indicator2'], 

        # 刻度线  线宽 width, 字号labelsize
        plt.tick_params(width=1, labelsize=12)
        
        # 调整坐标显示
        # plt.xlim(0, len(y1))
        # plt.ylim(0)
        # plt.xticks(range(0, len(y1), round(len(y1) / 20)))

        # 显示图片
        plt.show()


if __name__ == '__main__':
    '''句子处理'''
    # sentence0 = "当存在可燃性或有害气体时，应使用专用仪器进行检测，并应加强通风措施，气体浓度应控制在安全允许范围内。"
    sentence0 = "氮氧化物换算成二氧化氮不应超过5mg／m3。"
    # hanlp_progress(sentence0)
    hanlp_optimize_progress(sentence0)
    
    '''句子列表'''
    # Sentences_List = ['钢管片的螺栓孔应畅通，内圆面应平整；',
    #                   '管片贮存场地应坚实平整。',
    #                   '掘进施工应控制排土量、盾构姿态和地层变形。',
    #                   '管片严重开裂或严重错台；',
    #                   '对掘进施工影响范围内的岩溶和洞穴，应采取注浆等措施处理。',
    #                   '发生故障或运转不稳定；',
    #                   '应利用隧道内测量控制点采用极坐标法放样隧道中心线和盾构基座的位置、方向。应利用水准测量方法测设隧道高程控制线以及基座坡度。坐标和高程放样中误差为±5mm；',
    #                   '隧道结构监测初始值宜在管片壁后注浆凝固后12h内测量。']
    #
    # for sentence0 in Sentences_List:
    #     hanlp_optimize_progress(sentence0)  # 优化后结果
    
    '''文件处理, 可用于生成评估文件'''
    # in_file_name = r"data//test_pre.txt"
    # file_process(in_file_name)
    
    # # test = ReadFile()
    # # test.read_file(in_file_name)
    # # test.result_statistics()
    # # test.result_statistics_draw()