# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 20:31:32 2019

@author: ruan
"""

import codecs
import collections
from operator import itemgetter
import numpy as np
from pandas import DataFrame as dataframe
from pandas import Series as series
import os
import time
import tensorflow as tf
import logging
logging.basicConfig(level=logging.WARNING,format="[%(asctime)s] %(message)s",datefmt="%Y-%m-%d %H:%M:%S",)
from sklearn.model_selection import train_test_split
from neural_network import NeuralNetwork
import nn_lib

path_data = u'.\\data\\'
path_seq2seq = path_data+u'seq2seq_nmt\\'
# 源序列词库相关参数
vocab_size_src = 8000
path_corpus_src = path_seq2seq+'train.txt.en'
path_vocab_src = path_seq2seq+'en_vocab.pkl'
path_train_raw_src =  path_corpus_src
path_train_done_src =  path_seq2seq+'train.en'
# 目标序列词库相关参数
vocab_size_tgt = 4000
path_corpus_tgt = path_seq2seq+'train.txt.zh'
path_vocab_tgt = path_seq2seq+'zh_vocab.pkl'
path_train_raw_tgt =  path_corpus_tgt
path_train_done_tgt =  path_seq2seq+'train.zh'
# 超参数
word_embd_dim = 50
dim_rnn = word_embd_dim
learning_rate = 0.001
batch_size = 128
# 其它参数
test_mode = True

# 读取样本数据
def read_file(file_path):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    data = []
    for line in lines:
        data.append(line.strip().split())
        count += 1
        if test_mode is True:
            if count == 1000:
                break
    return data


#写入映射好id的样本数据
def write_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for sentence in data:
            f.write(sentence)
    return


#数据预处理
def preprocess_data(path_vocab, path_train_raw, path_train_done, src_or_tgt, max_len):
    # data = read_file(path_corpus)
    # word2id_vocab_,vocab_size_ = nn_lib.build_word2id_vocab(data,path_vocab,vocab_size=vocab_size)
    word2id_vocab, vocab_size = nn_lib.read_word2id_dict(path_vocab)
    data = read_file(path_train_raw)
    data_ = []
    for line in data:
        line_ = nn_lib.sentence2id(line, word2id_vocab)
        if 'source' == src_or_tgt:
            line_ = line_[:max_len-1]+[word2id_vocab['<EOS>']]
        elif 'target' == src_or_tgt:
            # line_ = [word2id_vocab['<SOS>']]+line_[:max_len-1]+[word2id_vocab['<EOS>']]
            line_ = line_[:max_len-1]+[word2id_vocab['<EOS>']]
        line_ = nn_lib.pad_seq(line_, max_len)
        data_.append(" ".join([str(id) for id in line_])+u"\n")
    write_file(path_train_done, data_)
    return data_


if __name__ == "__main__":
    # 构建字典
    if False:
        data_en = read_file(path_corpus_src)
        word2id_vocab_en, vocab_size_src = nn_lib.build_word2id_vocab(data_en, path_vocab_src, vocab_size=vocab_size_src)
        data_zh = read_file(path_corpus_tgt)
        word2id_vocab_zh, vocab_size_tgt = nn_lib.build_word2id_vocab(data_zh, path_vocab_tgt, vocab_size=vocab_size_tgt)
    # 预处理数据
    if False:
        data_src = preprocess_data(path_vocab_src, path_train_raw_src, path_train_done_src,
                                   src_or_tgt='source', max_len=200)
        data_tgt = preprocess_data(path_vocab_tgt, path_train_raw_tgt, path_train_done_tgt,
                                   src_or_tgt='target', max_len=100)
    # 初始化模型
    if True:
        x = read_file(path_train_done_src)
        x = np.array(x).astype(int)
        y = read_file(path_train_done_tgt)
        y = np.array(y).astype(int)
        random_seed = int(time.time())
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=random_seed)
        model = NeuralNetwork(x_train, y_train,
                              task_type='seq_generation', model_type='seq2seq',
                              loss_fun_type='cross_entropy', eval_score_type='cross_entropy', optimizer_type='Adam',
                              model_parameter={'keep_prob': 0.9,
                                               'train_or_infer': 'train',
                                               'dim_rnn': dim_rnn,
                                               'word_embd_dim': word_embd_dim,
                                               'encoder_word_embd_pretrain': None,
                                               'encoder_vocab_size': vocab_size_src,
                                               'decoder_word_embd_pretrain': None,
                                               'decoder_vocab_size': vocab_size_tgt,
                                               'batch_size': batch_size},
                              hyper_parameter={'learning_rate': learning_rate,
                                               'early_stop_rounds': 150},
                              other_parameter={'model_save_rounds': 50,
                                               'path_data': path_seq2seq}
                              )
        # 训练模型
        if False:
            model.train(transfer_learning=False, built_in_test=True, x_test=x_test, y_test=y_test)

        print(1)




