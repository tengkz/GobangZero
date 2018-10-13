#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 23:07:19 2018

@author: ubuntu
"""

from keras.models import Model
from keras.layers import Activation,BatchNormalization,Dense,Flatten,Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import add
from keras.optimizers import Adam
from keras.regularizers import l2

import pickle

class Net(object):
    def __init__(self,N,stage_num,kernel_size,memory_limit):
        self.N = N
        self.l2_const = 1e-4
        self.stage_num = stage_num
        self.kernel_size = kernel_size
        self.memory = []
        self.memory_limit = memory_limit
        self.create_net()
    
    def identity_block(self,input_tensor,stage):
        conv_name_base = 'res'+str(stage)+'_branch'
        bn_name_base = 'bn'+str(stage)+'_branch'
        
        x = input_tensor
        x = Conv2D(32,(self.kernel_size,self.kernel_size),padding='same',name=conv_name_base+'a')(x)
        x = BatchNormalization(axis=3,name=bn_name_base+'a')(x)
        x = Activation('relu')(x)
        
        x = Conv2D(32,(self.kernel_size,self.kernel_size),padding='same',name=conv_name_base+'b')(x)
        x = BatchNormalization(axis=3,name=bn_name_base+'b')(x)
        x = Activation('relu')(x)
        
        x = add([x,input_tensor])
        return x
    
    def create_net(self):
        src = Input((self.N,self.N,4))
        x = Conv2D(32,(self.kernel_size,self.kernel_size),padding='same',name='conv1')(src)
        x = BatchNormalization(axis=3,name='bn_conv1')(x)
        x = Activation('relu')(x)
        
        for i in range(self.stage_num):
            x = self.identity_block(x,stage=i+1)
        
        # policy net
        policy_net = Conv2D(2,(1,1))(x)
        policy_net = BatchNormalization(axis=3)(policy_net)
        policy_net = Activation('relu')(policy_net)
        policy_net = Flatten()(policy_net)
        policy_net = Dense(self.N*self.N,activation='softmax',name='distribution')(policy_net)
        
        # value net
        value_net = Conv2D(1,(1,1))(x)
        value_net = BatchNormalization(axis=3)(value_net)
        value_net = Activation('relu')(value_net)
        value_net = Flatten()(value_net)
        value_net = Dense(32,activation='relu')(value_net)
        value_net = Dense(1,activation='sigmoid',name='value_net')(value_net)
        
        self.model = Model(src,[policy_net,value_net])
        self.model.compile(Adam(lr=2e-4),['mean_squared_error','binary_crossentropy'])
    
    def policy_and_value(self,board):
        possible_moves = list(board.possible_moves_set)
        current_state = board.get_state()
        policy,value = self.model.predict(current_state.reshape(-1,self.N,self.N,4))
        policy = zip(possible_moves,policy.flatten()[possible_moves])
        return policy,value[0][0]
    
    def save_model(self,model_file):
        net_params = self.model.get_weights()
        pickle.dump(net_params,open(model_file,'wb'),protocol=2)
        
        