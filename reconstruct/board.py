# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 13:58:20 2018

@author: hztengkezhen
"""

import numpy as np

class Board(object):
    def __init__(self,N):
        self.N = N
        self.state = np.zeros([N*N],dtype=np.int32)
        self.possible_moves_set = set(range(N*N))
        self.turn = 1
        self.last = None
        self.step = 0
    
    def move(self,index):
        if index<0 or index>=self.N*self.N:
            print 'Move index illegal'
            raise ValueError
        self.step += 1
        self.state[index] = self.turn
        self.possible_moves_set.discard(index)
        self.turn = self.turn%2+1
        self.last = index
    
    def possible_moves(self):
        return list(self.possible_moves_set)
    
    def get_state(self):
        N = self.N
        np_state = np.zeros((4,N,N),dtype=np.float32)
        if self.step>0:
            index_current = np.where(self.state==self.turn)[0]
            index_last = np.where(self.state==(self.turn%2+1))[0]
            np_state[0][index_current/N,index_current%N] = 1.0
            np_state[1][index_last/N,index_last%N] = 1.0
            np_state[2][self.last//N,self.last%N] = 1.0
        if self.step%2==0:
            np_state[3][:,:] = 1.0
        return np_state
    
    def is_finish(self):
        N = self.N
        for index in np.where(self.state>0)[0]:
            row,col = index//N,index%N
            if col<=N-5 and self.state[index:(index+5)].prod() in (1,32):
                return True,self.turn%2+1
            if row<=N-5 and self.state[range(index,index+5*N,N)].prod() in (1,32):
                return True,self.turn%2+1
            if col<=N-5 and row<=N-5 and self.state[range(index,index+5*(N+1),N+1)].prod() in (1,32):
                return True,self.turn%2+1
            if col>=4 and row<=N-5 and self.state[range(index,index+5*(N-1),N-1)].prod() in (1,32):
                return True,self.turn%2+1
        if self.step>=N*N:
            return False,-1
        return False,0
    
    def copy(self):
        b = Board(self.N)
        b.state = self.state.copy()
        b.step = self.step
        b.possible_moves_set = self.possible_moves_set.copy()
        b.turn = self.turn
        b.last = self.last
        return b
    
    def show(self):
        for row in range(self.N):
            print ''.join([str(item) for item in self.state[row*self.N:(row+1)*self.N]])
    

class Game(object):
    def __init__(self,N):
        self.N = N
        self.board = None
    
    def initialize_game(self):
        self.board = Board(self.N)
    
    def game_start(self,player1,player2):
        self.initialize_game()
        N = self.N
        while self.board.step<N*N:
            if self.board.step%2==0:
                move = player1.pick_move(self.board)
            else:
                move = player2.pick_move(self.board)
            self.board.move(move)
            win,winner = self.board.is_finish()
            if win:
                self.board.show()
                return winner
        return -1
    
    def self_play(self,player):
        return self.game_start(player,player)

class Random_player(object):
    def pick_move(self,board):
        return np.random.choice(board.possible_moves(),1)[0]
