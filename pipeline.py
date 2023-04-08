from hanlp_model_conf_new import ReadFile
from config.help_functions_new import *
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import linecache
import json


def read_config():
    with open(r"config.json",encoding="utf-8") as json_file:
        config = json.load(json_file)
    return config

config = read_config() # 读取配置文件

sentence_categories = config["categories"]
classification_rules = [v for _, v in config["regex rules"].items()]
match_patterns = [v for _, v in config["match patterns"].items()]


if __name__ == '__main__':
    
    '''文件批量处理'''
    # test = ReadFile()
    
    # list_file = []  # 存放文件名称
    # with tqdm(list_file) as t1:
    #     for in_file_name in t1:
    #         t1.set_description('Processed')
    
    '''文件处理'''
    in_file_name = r"data//kg_test.txt"
    new_document_path = 'result'
    _file_name = Path(in_file_name).stem  # 去掉文件后缀,短路径
    out_file_name = _file_name + "_pipeline_result"
    
    test = ReadFile()
    K_Ds = pd.DataFrame() # 构造空DataFrame
    
    with open(in_file_name, "r", encoding="utf-8") as f1:
        for line in f1.readlines():
        
        # # with tqdm(f1.readlines(), desc=f"{_file_name} @processing", position=0) as t:
        # #     for line in t:
        
    # line = linecache.getline(in_file_name, 1)
    
            line_processed, clause_number = sentence_id_preprocess(line)
            sents = split_sentence(line_processed)  # 分句
            # print(sents)
            
            for sent in sents:
                print("Sentence:", sent)
                Clause_Type = type_analyze(sent, sentence_categories, classification_rules)  # 条文分类
                print("Clause_Type:", Clause_Type)
                if Clause_Type == "未分类":
                    pass
                else:
                    if Clause_Type == "术语类":
                        shuyu_parse(sent)
                    else:
                        # SRL处理
                        list_optimalsrl = test.hanlp_optimize_progress(sent)[-1]
                        if list_optimalsrl:
                            # 模式匹配: 针对单个SRL组进行匹配处理
                            for s in list_optimalsrl:
                                D = pattern_match(Clause_Type, s, sentence_categories, match_patterns)
                                print()
                                if D.empty: # 判断DataFrame是否为空
                                    pass
                                else:
                                    K_Ds = pd.concat([K_Ds, D],ignore_index=True) # 竖向连接DataFrame
                                    # ignore_index=True, 合并后不保留原索引，启用新的自然索引
                                    
    print("模式匹配后知识元组个数:", len(K_Ds))
    # print(test.List_Evaluation_Indicator_1)
    # print(test.List_Evaluation_Indicator_2)
    # test.result_statistics()
    # test.result_statistics_draw()

    # # 写入 EXCEL 数据
    # file_name = new_document_path + "//" + out_file_name + ".xlsx"
    # with pd.ExcelWriter(file_name) as writer:   # , mode='a', if_sheet_exists="new"
    #     K_Ds.to_excel(writer, index=False)

    # # 写入 CSV 数据
    # file_name = new_document_path + "//" + out_file_name + ".csv"
    # K_Ds.to_csv(file_name, sep=',', index=False, header=True, encoding='utf-8')

    # # 写入 JSON 数据
    # file_name = new_document_path + "//" + out_file_name + ".json"
    # K_Ds.to_json(file_name, orient ='index', indent=4, force_ascii=False)  # records
    