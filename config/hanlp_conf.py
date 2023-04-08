import hanlp


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


def model_configuration(_way="U", _tok_granularity='tok/fine', _pos='pos/pku',
                        user_dict_paths=None, user_dynamic_dictionary=None):
    """模型及处理方式选择
        _way="U",默认多任务联合模型处理;可选_way="P",管道模型处理;
        tok_granularity='tok/fine',默认细粒度分词;可选tok_granularity='tok/coarse',进行粗粒度分词.
        _pos= ”pos/pku“,默认进行pku词性标注; 可选_pos= ”pos/ctb“,ctb标准.
    """

    if _way == "P":
        _HanLP = hanlp.pipeline()
        if _tok_granularity == "tok/coarse":
            tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
        else:
            '''默认细粒度分词处理'''
            tok = hanlp.load(hanlp.pretrained.tok.FINE_ELECTRA_SMALL_ZH)

        if user_dict_paths:
            tok.dict_combine = tok_custom_dict(user_dict_paths)
        else:
            if user_dynamic_dictionary:
                tok.dict_combine = user_dynamic_dictionary  # 自定义词典集合
            else:
                tok.dict_force = tok.dict_combine = None

        _HanLP.append(tok, output_key=_tok_granularity)

        if _pos == 'pos/ctb':
            pos = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
        else:
            '''默认'pos/pku 词性标注'''
            pos = hanlp.load(hanlp.pretrained.pos.PKU_POS_ELECTRA_SMALL)

        _HanLP.append(pos, input_key=_tok_granularity, output_key=_pos)

        srl = hanlp.load('CPB3_SRL_ELECTRA_SMALL', conll=0)
        _HanLP.append(srl, input_key=_tok_granularity, output_key='srl')

    else:
        '''联合抽取模型'''
        # _HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
        # _HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH)
        _HanLP = U_model
        try:
            tok = _HanLP[_tok_granularity]
        except:
            print("选取的预训练模型不支持该任务")
            raise
        if user_dict_paths:
            tok.dict_combine = tok_custom_dict(user_dict_paths)
        else:
            if user_dynamic_dictionary:
                tok.dict_combine = user_dynamic_dictionary  # 自定义词典集合
            else:
                tok.dict_force = tok.dict_combine = None

        tasks = list(_HanLP.tasks.keys())
        for task in tasks:
            try:
                if task not in (_tok_granularity, _pos, 'srl'):
                    del _HanLP[task]
            except:
                print("选取的预训练模型不支持该任务")
                raise
    return _HanLP


'''自定义模型配置，得到HanLP'''

# user_dictionary_path = "dict.txt"  # 自定义词典
# user_dict_set = {}

user_dictionary_path = None
user_dict_set = {'不应', '不得', '不宜', '盾构', '滚转角', '工作井', '注浆', '注浆口', '注浆量', '一般项目',
                 '控制点', '水准测量', '测量较差', '放样', '相适应', '验算', '可调', '可配置', '测设', '过站', '调头',
                 '持证上岗', '漏涂', '漏浆', '套箍', '遇水膨胀防水材料', '衬砌结构', '缺棱掉角', '易于压注',
                 '注浆孔', "排土量", "始发", "复测", "迁站", "压面", "施焊", "壁后注浆", "管片", "混凝土"}

U_model = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
# U_model = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH)

HanLP = model_configuration(_way="U", 
                            _tok_granularity='tok/fine',
                            _pos='pos/pku',
                            user_dict_paths=user_dictionary_path, 
                            user_dynamic_dictionary=user_dict_set)

'''原始模型'''

# # 联合处理模型
# HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH)
# HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
