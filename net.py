#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 11:50:08 2018

@author: ubuntu
"""
import itertools
import random
import numpy as np

from keras.models import Model
from keras.layers import Activation,BatchNormalization,Dense,Flatten,Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import add
from keras.optimizers import Adam

import joblib

MEMORY_SIZE = 30000

class ResNet(object):
    def __init__(self,input_kernel_num=32,process_kernel_num=32,
                 stage_num=2,kernel_width=3,kernel_height=3):
        self.input_kernel_num = input_kernel_num
        self.process_kernel_num = process_kernel_num
        self.stage_num = stage_num
        self.kernel_width = kernel_width
        self.kernel_height = kernel_height
    
    def create(self,width,height,channel_num):
        src = Input(shape=(width,height,channel_num))
        # src->Conv2D->BN->Activation
        x = src
        x = Conv2D(self.input_kernel_num,(self.kernel_width,self.kernel_height),
                   padding='same',name='conv1')(x)
        x = BatchNormalization(axis=3,name='bn_conv1')(x)
        x = Activation('relu')(x)
        
        for i in range(self.stage_num):
            x = self.identity_block(x,self.process_kernel_num,
                                    stage=i+1)
        self.model = Model(src,x)
        return self.model
    
    def identity_block(self,input_tensor,filter_num,stage):
        conv_name_base = 'res'+str(stage)+'_branch'
        bn_name_base = 'bn'+str(stage)+'_branch'
        
        # Conv2D->BN->Activate->Conv2D->BN->Activate
        x = input_tensor
        x = Conv2D(filter_num,(self.kernel_width,self.kernel_height),
                   padding='same',name=conv_name_base+'a')(x)
        x = BatchNormalization(axis=3,name=bn_name_base+'a')(x)
        x = Activation('relu')(x)
        
        x = input_tensor
        x = Conv2D(filter_num,(self.kernel_width,self.kernel_height),
                   padding='same',name=conv_name_base+'b')(x)
        x = BatchNormalization(axis=3,name=bn_name_base+'b')(x)
        x = Activation('relu')(x)
        
        x = add([x,input_tensor])
        return x

class GobangModel(object):
    def __init__(self,N,batch_size=128,max_fit_samples=512):
        self.N = N
        self.batch_size = batch_size
        self.max_fit_samples = max_fit_samples
        self.train_archive = []
        self.model_name = 'Gobang-v0'
        print self.model_name
    
    def create(self):
        N = self.N
        resnet = ResNet()
        resnet.create(N,N,3)
        src = Input((N,N,3))
        x = resnet.model(src)
        
        # Conv2D->BN->AC->Flatten->Dense
        dist = Conv2D(2,(1,1))(x)
        dist = BatchNormalization(axis=3)(dist)
        dist = Activation('relu')(dist)
        dist = Flatten()(dist)
        dist = Dense(N*N+1,activation='softmax',name='distribution')(dist)
        
        # Conv2D->BN->AC->Flatten->Dense->Dense
        result = Conv2D(1,(1,1))(x)
        result = BatchNormalization(axis=3)(result)
        result = Activation('relu')(result)
        result = Flatten()(result)
        result = Dense(256,activation='relu')(result)
        result = Dense(1,activation='sigmoid',name='result')(result)
        
        self.model = Model(src,[dist,result])
        self.model.compile(Adam(lr=2e-2),['mean_squared_error','binary_crossentropy'])
        self.model.summary()
    
    def fit_game(self,positions,dists,result):
        this_game = []
        for pos,dist in zip(positions,dists):
            this_game.append((pos,dist,result))
            result = -result
        #joblib.dump(this_game,'dump.joblib',compress=5)
        print 'Attention!!! this game length is %d' % len(this_game)
        self.train_archive.extend(this_game)
        
        if len(self.train_archive)>MEMORY_SIZE:
            self.train_archive = self.train_archive[-MEMORY_SIZE:]
            print 'Attention!!! train_archive change'
            
        if len(self.train_archive) >= self.max_fit_samples:
            archive_samples = random.sample(self.train_archive,self.max_fit_samples)
        else:
            archive_samples = self.train_archive
        X_fit_samples = list(itertools.chain(this_game,archive_samples))
        X_shuffled = random.sample(X_fit_samples,len(X_fit_samples))
        
        X,y_dist,y_result = [],[],[]
        for pos,dist,result in X_shuffled:
            X.append(pos)
            y_dist.append(dist)
            y_result.append(float(result)/2.0+0.5)
            if len(X) % self.batch_size == 0:
                errors = self.model.train_on_batch(np.array(X),[np.array(y_dist),np.array(y_result)])
                print "Training error: ",errors
                X,y_dist,y_result = [],[],[]
        if len(X)>0:
            errors = self.model.train_on_batch(np.array(X),[np.array(y_dist),np.array(y_result)])
            print "Training error: ",errors
    
    def predict(self,position):
        dist,res = self.model.predict(position)
        res = np.array([r[0]*2-1 for r in res])
        return [dist[0,:],res[0]]
    
    def predict_distribution(self,position):
        dist,res = self.predict(position)
        return dist
    
    def predict_winrate(self,position):
        dist,res = self.predict(position)
        return res
    
    def save(self,snapshot):
        self.model.save_weights('weights-snapshot-%d.h5' % snapshot)
    
    def load(self,snapshot):
        self.model.load_weights('weights.h5')
