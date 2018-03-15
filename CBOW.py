# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 12:58:28 2018

@author: windows


"""
import random
import tensorflow as tf
import numpy as np
import math
import collections
import pickle as pkl
from pprint import pprint
#from pymongo import MongoClient
import re
import jieba
import os.path as path
import os

class word2vec():
    def __init__(self,
                 vocab_list=None,
                 embedding_size=None,
                 win_len=None, # 单边窗口长
                 num_sampled=None,
                 learning_rate=None,
                 logdir=None,
                 model_path= None
                 ):

        # 获得模型的基本参数
        self.batch_size     = None # 一批中数据个数, 目前是根据情况来的
        if model_path!=None:
            self.load_model(model_path)
        else:
            # model parameters
            assert type(vocab_list)==list
            self.vocab_list     = vocab_list
            self.vocab_size     = vocab_list.__len__()+1
            self.embedding_size = embedding_size
            self.win_len        = win_len
            self.num_sampled    = num_sampled
            self.learning_rate  = learning_rate
            self.logdir         = logdir
            ##############################################################################
            #self.valid_size     = 16  # Random set of words to evaluate similarity on.
            #self.valid_window   = 100  # Only pick dev samples in the head of the distribution.
            #self.valid_examples = np.array(random.sample(range(self.valid_window), self.valid_size))
            ##############################################################################
            
            self.word2id = {}   # word => id 的映射
            for i in range(self.vocab_size):
                if(i!=self.vocab_size-1):
                    # i == self.vocab_size-1 is reserved for null id
                    self.word2id[self.vocab_list[i]] = i
                else:
                    break


            # train times
            self.train_words_num = 0 # 训练的单词对数
            self.train_sents_num = 0 # 训练的句子数
            self.train_times_num = 0 # 训练的次数（一次可以有多个句子）

            # train loss records
            self.train_loss_records = collections.deque(maxlen=10) # 保存最近10次的误差
            self.train_loss_k10 = 0

        self.build_graph()
        self.init_op()
        if model_path!=None:
            tf_model_path = os.path.join(model_path,'tf_vars')
            self.saver.restore(self.sess,tf_model_path)

    def init_op(self):
        self.sess = tf.Session(graph=self.graph)
        self.sess.run(self.init)
        self.summary_writer = tf.summary.FileWriter(self.logdir, self.sess.graph)

    def build_graph(self):
        self.graph = tf.Graph()
        with self.graph.as_default():
            '''
    # Input data.
    train_inputs = tf.placeholder(tf.int32, shape=[2 * self.win_len, batch_size])
    train_labels = tf.placeholder(tf.float32, shape=[batch_size, 1])
    valid_dataset = tf.constant(valid_examples, shape=[2 * self.win_len, batch_size], dtype=tf.int32)

    # Variables.
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    softmax_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size],
                            stddev=1.0 / math.sqrt(embedding_size)))
    softmax_biases = tf.Variable(tf.zeros([vocabulary_size]))

    # Model.
    # Look up embeddings for inputs.
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)
    # sum up vectors on first dimensions, as context vectors
    embed_sum = tf.reduce_sum(embed, 0)

    # Compute the softmax loss, using a sample of the negative labels each time.
    loss = tf.reduce_mean(
        tf.nn.sampled_softmax_loss(softmax_weights, softmax_biases,
                                   train_labels, embed_sum,
                                   num_sampled, vocabulary_size))

    # Optimizer.
    optimizer = tf.train.AdagradOptimizer(1.0).minimize(loss)

    # Compute the similarity between minibatch examples and all embeddings.
    # We use the cosine distance:
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
    normalized_embeddings = embeddings / norm
    valid_embeddings = tf.nn.embedding_lookup(
        normalized_embeddings, valid_dataset)
    # sum up vectors
    valid_embeddings_sum = tf.reduce_sum(valid_embeddings, 0)
    similarity = tf.matmul(valid_embeddings_sum, tf.transpose(normalized_embeddings))          
            
            
            '''
            self.train_inputs = tf.placeholder(tf.int32, shape=[2 * self.win_len, self.batch_size])
            #self.train_inputs = tf.placeholder(tf.int32, shape=[self.batch_size])
            self.train_labels = tf.placeholder(tf.int32, shape=[self.batch_size, 1])
            #self.valid_dataset = tf.constant(self.valid_examples, shape=[2 * self.win_len, self.batch_size], dtype=tf.int32)

            self.embedding_dict = tf.Variable(
                tf.random_uniform([self.vocab_size,self.embedding_size],-1.0,1.0)
            )
            self.softmax_weights = tf.Variable(tf.truncated_normal([self.vocab_size, self.embedding_size],
                                                              stddev=1.0/math.sqrt(self.embedding_size)))
            self.softmax_biases = tf.Variable(tf.zeros([self.vocab_size]))
                
            # 将输入序列向量化 4'30''
            #embedding_dict 大词向量表  #train_inputs 一个batch输入的单词id
            # 将输入序列向量化
            ## embed是啥
                    # Model.



            embed = tf.nn.embedding_lookup(self.embedding_dict, self.train_inputs) # batch_size
            # sum up vectors on first dimensions, as context vectors
            embed_sum = tf.reduce_sum(embed, 0)
            
            # Compute the softmax loss, using a sample of the negative labels each time.
            self.loss = tf.reduce_mean(
                tf.nn.sampled_softmax_loss(
                    weights = self.softmax_weights,
                    biases = self.softmax_biases,
                    labels = self.train_labels,
                    inputs = embed_sum,
                    num_sampled = self.num_sampled,
                    num_classes = self.vocab_size
                )
            )

            # tensorboard 相关 tf.scalar_summary

            tf.summary.scalar('loss',self.loss)  # 让tensorflow记录参数

            ####
            # Optimizer.
            self.train_op = tf.train.AdagradOptimizer(learning_rate=0.1).minimize(self.loss)  # 训练操作
            ###
            
            # Compute the similarity between minibatch examples and all embeddings.
            # We use the cosine distance:

            # 计算与指定若干单词的相似度
            self.test_word_id = tf.placeholder(tf.int32,shape=[None])
            vec_l2_model = tf.sqrt(  # 求各词向量的L2模
                tf.reduce_sum(tf.square(self.embedding_dict),1,keep_dims=True)
            )

            avg_l2_model = tf.reduce_mean(vec_l2_model)
            tf.summary.scalar('avg_vec_model',avg_l2_model)

            self.normed_embedding = self.embedding_dict / vec_l2_model
            # self.embedding_dict = norm_vec # 对embedding向量正则化
            test_embed = tf.nn.embedding_lookup(self.normed_embedding, self.test_word_id)
            self.similarity = tf.matmul(test_embed, self.normed_embedding, transpose_b=True)




            # 变量初始化
            self.init = tf.global_variables_initializer()

            self.merged_summary_op = tf.summary.merge_all()

            self.saver = tf.train.Saver()

    def train_by_sentence(self, input_sentence=[]):
        '''
    win_len=2
    ##
    span=win_len*2-1
    ##
    #sent_num = input_sentence.__len__()
    batch_inputs = []
    batch_labels = []
    for sent in input_sentence:                     #sent:['噢', '天', '上帝', '求求', '你别', '散发', '魅力']
        for i in range(sent.__len__()):
            start = max(0,i-win_len)
            end = min(sent.__len__(),i+win_len+1)
            win_inputs=[]
            for index in range(start,end):          #在上下文区间遍历
                #print(index)
                if index == i:                      #去掉除了上下文的当前词
                    #print(i)
                    batch_labels.append(sent[i])

                else:

                    win_inputs.append(sent[index])
            
            
            if(len(win_inputs)<span+1):
                for i in range(span-len(win_inputs)+1):
                    win_inputs.append(0)
            batch_inputs.append(win_inputs)                       #输入词id传入batch中        
        '''
        # 输入当前已经分好词的句子
        span=self.win_len*2-1
        sent_num = input_sentence.__len__()
        batch_inputs = []
        batch_labels = []
        for sent in input_sentence:                     #sent:['噢', '天', '上帝', '求求', '你别', '散发', '魅力']
            for i in range(sent.__len__()):
                start = max(0,i-self.win_len)
                end = min(sent.__len__(),i+self.win_len+1)
                win_inputs=[]
                for index in range(start,end):          #在上下文区间遍历
                    if index == i:                      #去掉除了上下文的当前词
                    ##################################get default return null id: default=self.vocab_size-1
                        label_id=self.word2id.get(sent[i])
                        if label_id is None:
                            # if current word does not exist in top 90% frequency vocab_list
                            # add null id [vocab_size-1]
                            batch_labels.append(self.vocab_size-1)
                        else:
                            batch_labels.append(label_id)

                        #continue
                    else:                               #不一致则输入上下文
                        input_id=self.word2id.get(sent[index])
                        if input_id is None:
                            # if current word does not exist in top 90% frequency vocab_list
                            # add null id [vocab_size-1]
                            win_inputs.append(self.vocab_size-1)
                        else:
                            win_inputs.append(input_id)
           
                if(len(win_inputs)<span+1):
                    for i in range(span-len(win_inputs)+1):
                        ##########################################################
                        # self.vocab_size-1 is reserved for null type to keep the shape of batch_inputs is (win_len*2,?)
                        win_inputs.append(self.vocab_size-1)
                        #########################################################
                batch_inputs.append(win_inputs)                       #输入词id传入batch中 
                
                if len(batch_inputs)==0:
                    return
        #使用numpy把行转换为列
        batch_inputs = np.array(batch_inputs,dtype=np.int32).T                #int32因为是id值
        batch_labels = np.array(batch_labels,dtype=np.int32)
        batch_labels = np.reshape(batch_labels,[batch_labels.__len__(),1])  #行->列
        # len(batch_inputs)>0: check if context of current word is null
        if len(batch_inputs)>0 and len(batch_inputs.T)>0:
            feed_dict = {
                self.train_inputs: batch_inputs,
                self.train_labels: batch_labels
            }
            _, loss_val, summary_str = self.sess.run([self.train_op,self.loss,self.merged_summary_op], feed_dict=feed_dict)
            #self.train_op迭代得到损失值
            # train loss
            self.train_loss_records.append(loss_val)
            # self.train_loss_k10 = sum(self.train_loss_records)/self.train_loss_records.__len__()
            self.train_loss_k10 = np.mean(self.train_loss_records)
            if self.train_sents_num % 1000 == 0 :
                self.summary_writer.add_summary(summary_str,self.train_sents_num)
                print("{a} sentences dealed, loss: {b}"
                      .format(a=self.train_sents_num,b=self.train_loss_k10))
    
            # train times
            #打印训练内容
            self.train_words_num += batch_inputs.__len__()
            self.train_sents_num += input_sentence.__len__()
            self.train_times_num += 1

    #计算相似度
    def cal_similarity(self,test_word_id_list,top_k=10):
        sim_matrix = self.sess.run(self.similarity, feed_dict={self.test_word_id:test_word_id_list})
        sim_mean = np.mean(sim_matrix)
        sim_var = np.mean(np.square(sim_matrix-sim_mean))
        test_words = []
        near_words = []
        for i in range(test_word_id_list.__len__()):
            #id传进来
            test_words.append(self.vocab_list[test_word_id_list[i]])
            nearst_id = (-sim_matrix[i,:]).argsort()[1:top_k+1]
            #id->word
            nearst_word = [self.vocab_list[x] for x in nearst_id]
            near_words.append(nearst_word)
        return test_words,near_words,sim_mean,sim_var

    def save_model(self, save_path):

        if os.path.isfile(save_path):
            raise RuntimeError('the save path should be a dir')
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        # 记录模型各参数
        model = {}
        var_names = ['vocab_size',      # int       model parameters
                     'vocab_list',      # list
                     'learning_rate',   # int
                     'word2id',         # dict
                     'embedding_size',  # int
                     'logdir',          # str
                     'win_len',         # int
                     'num_sampled',     # int
                     'train_words_num', # int       train info
                     'train_sents_num', # int
                     'train_times_num', # int
                     'train_loss_records',  # int   train loss
                     'train_loss_k10',  # int
                     ]
        for var in var_names:
            model[var] = eval('self.'+var)

        param_path = os.path.join(save_path,'params.pkl')
        if os.path.exists(param_path):
            os.remove(param_path)
        with open(param_path,'wb') as f:
            pkl.dump(model,f)

        # 记录tf模型
        tf_path = os.path.join(save_path,'tf_vars')
        if os.path.exists(tf_path):
            os.remove(tf_path)
        self.saver.save(self.sess,tf_path)

    def load_model(self, model_path):
        if not os.path.exists(model_path):
            raise RuntimeError('file not exists')
        param_path = os.path.join(model_path,'params.pkl')
        with open(param_path,'rb') as f:
            model = pkl.load(f)
            self.vocab_list = model['vocab_list']
            self.vocab_size = model['vocab_size']
            self.logdir = model['logdir']
            self.word2id = model['word2id']
            self.embedding_size = model['embedding_size']
            self.learning_rate = model['learning_rate']
            self.win_len = model['win_len']
            self.num_sampled = model['num_sampled']
            self.train_words_num = model['train_words_num']
            self.train_sents_num = model['train_sents_num']
            self.train_times_num = model['train_times_num']
            self.train_loss_records = model['train_loss_records']
            self.train_loss_k10 = model['train_loss_k10']
           
if __name__=='__main__':
    # step 1 读取停用词
    #停用词：并不希望使用的无意义的词 e.g你的铅笔 我吃饭了 ‘的’‘了’
    print(1)
    stopWords=[]
    path=r'E:\自然语言处理\代码\tensorflow-word2vec'
    name='stopwords.txt'
    with open(path+'\\'+name,encoding='utf-8') as f:
        line=f.readline()
        while line:#只要line中有东西，就一点点往里面存
            stopWords.append(line[:-1])
            #[:-1]去掉每一行的换行符 \n
            line=f.readline()
            
        #去掉重复的值
        stopWords=set(stopWords)
        print(stopWords)

    print('停用词读取完毕，共{n}个单词'.format(n=len(stopWords)))

    # step2 读取文本，预处理，分词，得到词典
    raw_word_list = []
    sentence_list = []
    #Comment_New.txt 'utf-8'
    with open('Comment_New.txt',encoding='utf-8') as f:
        line = f.readline()
        while line:
            #每一行的换行符\n去掉
            while '\n' in line:
                line = line.replace('\n','')

           
            #while '!' in line:
                #line = line.replace('!','')             
            #每一行的空格\n去掉 
            #while ' ' in line:
                #line = line.replace(' ','')
            #去掉标点符号remove all symbol in comment
           #\d number
           #\w English char
           #\u4e00-\u9fa5 Chinese char
            if re.findall(u'[^\u4e00-\u9fa5]+',line):  
                tmp=re.findall(u'[^\u4e00-\u9fa5]+',line)
                for i in tmp:
                    line=line.replace(i,' ')
            if len(line)>0: # 如果句子非空
                #jieba.cut(line,cut_all=False) 一行分词结果传入list
                raw_words = list(jieba.cut(line,cut_all=False))
                #
                dealed_words = []
                for word in raw_words:
                    #word不在停用词中                   
                    if word not in stopWords and word not in ['www','com','http']:
                        print(word)
                        raw_word_list.append(word)
                        #raw_word_list: all words in file [word1,word2,....,wordn]
                        dealed_words.append(word)
                        #dealed_words: words in current line
                sentence_list.append(dealed_words)
            #读下一行
            line = f.readline()
    print(sentence_list)
    #[[word1,word2,...],[word1,word2,..]]

    word_count = collections.Counter(raw_word_list)
    #raw_word_list中的单词去重后放入word_count
    #collections.Counter 可以用来统计词频
    print('文本中总共有{n1}个单词,不重复单词数{n2},选取前15000个单词进入词典'
          .format(n1=len(raw_word_list),n2=len(word_count)))
          #文本中总共有523496个单词,不重复单词数45475,选取前35000个单词进入词典
          
    #针对提取的部分单词出现较少的情况（生僻词），使用most_common(n)过滤
    #word_count是根据词频排序的词汇表
    #most_common(n)提取最常见的n个词 
    #word_count = word_count.most_common(100)
    
    word_count = word_count.most_common(15000)
    #word_count.most_common(10)后是一个词对应一个词频
    #word_count变成元祖列表[('哈哈哈', 12),('厉害', 4),(),...]
    #只拿第一维x[0]把单词拿出来
    word_list = [x[0] for x in word_count]
    #word_list 把所有最常见的30000词按照词频顺序拿到手了
    print(word_list)

    #word2vec类
    # 创建模型，训练
    w2v = word2vec(vocab_list=word_list,    #   词典集 （语料库）
                   embedding_size=300,      #   词向量维度 不能动
                   win_len=4,               #   滑动窗口 越大越好
                   learning_rate=1,         #   学习率 越小越好
                   num_sampled=100,         # 负采样个数 不能动
                   logdir='/tmp/simple_word2vec')       # tensorboard记录地址
                   
                   
    num_steps = 10000
    for i in range(num_steps):
        #print (i%len(sentence_list))
        #sentence_list [[word1,word2,...],[word1,word2,..]]
        sent = sentence_list[i%len(sentence_list)]  #一句一句拿出来
        w2v.train_by_sentence([sent])               #训练函数 输入当前已经分好词的句子
    w2v.save_model('model')
    #保存模型  
    w2v.load_model('model') 
    test_word = ['北京','冬奥会','中国','冠军','韩国','裁判','犯规','辣鸡']
    test_id = [word_list.index(x) for x in test_word]
    #计算相似度
    test_words,near_words,sim_mean,sim_var = w2v.cal_similarity(test_id)
    print (test_words,near_words,sim_mean,sim_var)




