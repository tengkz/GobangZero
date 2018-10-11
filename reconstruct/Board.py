# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 13:58:20 2018

@author: hztengkezhen
"""

import numpy as np

class Board(object):
    def __init__(self,N):
        self.N = N
        self.state = np.zeros([N,N])
        self.possible_moves = set(range(N*N))
        self.turn = 'A'
        self.last = None
        self.step = 0
    
    def move(self,index):
        if index<0 or index>=self.N*self.N:
            print 'Move index illegal'
            raise ValueError
        self.step += 1
        self.state[self.step] = index
        self.possible_moves.discard(index)
        self.turn.swapcase()
        self.last = index
    
    def get_state(self):
        N = self.N
        np_state = np.zeros((4,N,N))
        if self.step>0:
            if self.turn=='A':
                A_moves,a_moves = self.state[0:N*N:2],self.state[1:N*N:2]
            else:
                a_moves,A_moves = self.state[0:N*N:2],self.state[1:N*N:2]
            np_state[0][A_moves//N,A_moves%N] = 1.0
            np_state[1][a_moves//N,a_moves%N] = 1.0
            np_state[2][self.last//N,self.last%N] = 1.0
        if self.step%2==0:
            np_state[3][:,:] = 1.0
        return np_state
    
    def is_finish(self):
            
            
            