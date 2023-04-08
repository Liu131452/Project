import hanlp
# print(hanlp.pretrained.tok.ALL)  # 查看预训练模型
HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
# HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH)

# %%
sentence = "一氧化碳不应超过30mg／m3。"
# sentence ="当盾构到达接收工作井100m时，应对盾构姿态进行测量和调整。"
# sentence = "粉尘容许浓度，空气中含有10％及以上的游离二氧化硅的粉尘不得大于2mg／m3，空气中含有10％以下的游离二氧化硅的矿物性粉尘不得大于4mg／m3。"
print(sentence)

# %%  自定义词典:合并模式
tok = HanLP['tok/coarse']  # ['tok/fine']
tok.dict_force = None
tok.dict_combine = {'不应', '并应', '不得', '不宜', '盾构', '滚转角', '工作井', '注浆', '注浆口', "排土量", "掘进施工"}

# %%  粗粒度，粗粒度需要skip
sentence_nlp = HanLP(sentence, tasks=['tok/coarse', 'pos/pku', 'srl'], skip_tasks=['tok/fine'])
sentence_pos_show = HanLP(sentence, tasks=['tok/coarse', 'pos/pku'], skip_tasks=['tok/fine'])
# print(sentence_nlp['tok/coarse'])
sentence_pos_show.pretty_print()

# %%  细粒度
sentence_nlp = HanLP(sentence, tasks=['tok/fine', 'pos/pku', 'srl'], skip_tasks=['tok/coarse'])
sentence_pos_show = HanLP(sentence, tasks=['tok/fine', 'pos/pku'], skip_tasks=['tok/coarse'])
# print(sentence_nlp['tok/fine'])
sentence_pos_show.pretty_print()

# %%  传入分词结果进行处理: :param  sentence_tok(分词列表)
# sentence_nlp = HanLP(sentence_tok, tasks=['pos/pku', 'srl'], skip_tasks=['tok*'])
# sentence_pos_show = HanLP(sentence_tok, tasks=['pos/pku'], skip_tasks=['tok*'])
# print(sentence_nlp)
# sentence_pos_show.pretty_print()

# # %% 管道方式 pipeline
# HanLP = hanlp.pipeline()
#
# tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)  # '''粗粒度'''
# # tok = hanlp.load(hanlp.pretrained.tok.FINE_ELECTRA_SMALL_ZH)  # '''细粒度'''
# HanLP.append(tok, output_key='tok')

# # pos = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)   # '''pos/ctb'''
# pos = hanlp.load(hanlp.pretrained.pos.PKU_POS_ELECTRA_SMALL)  # '''默认'pos/pku 词性标注'''
# HanLP.append(pos, input_key='tok', output_key='pos')
#
# srl = hanlp.load('CPB3_SRL_ELECTRA_SMALL', conll=0)
# HanLP.append(srl, input_key='tok', output_key='srl')
#
# sentence_nlp = HanLP(sentence)
# print(sentence_nlp['srl'])

# %%
# print(sentence_nlp['srl'])
# print()
# print("initial_srl_result:")  # 原始结果
# for i in sentence_nlp['srl']:
#     print(i)
#     for j in i:
#         print(j[0:2])
#     print()

