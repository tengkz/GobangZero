#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 09:41:33 2018

@author: ubuntu
"""
import random

N = 13

empty_board = '.'*N*N

def show_board(board):
    board_showed = [board[i:(i+N)] for i in range(0,N*N,N)]
    print '\n'.join(board_showed)

def to_index(row,col):
    return row*N+col

def to_row_col(index):
    return index//N,index%N

def make_board(board):
    for i in range(5):
        index = to_index(18-i,i)
        board = ''.join([board[:index],'A',board[index+1:]])
    return board

def _win_horizontal(board,row,col,turn):
    if col>N-5:
        return False
    for i in range(4):
        if board[to_index(row,col+i+1)]!=turn:
            return False
    return True

def _win_vertical(board,row,col,turn):
    if row>N-5:
        return False
    for i in range(4):
        if board[to_index(row+i+1,col)]!=turn:
            return False
    return True

def _win_diag(board,row,col,turn):
    if row>N-5 or col>N-5:
        return False
    for i in range(4):
        if board[to_index(row+i+1,col+i+1)]!=turn:
            return False
    return True

def _win_diag2(board,row,col,turn):
    if row>N-5 or col<4:
        return False
    for i in range(4):
        if board[to_index(row+i+1,col-i-1)]!=turn:
            return False
    return True

def _win(board,turn):
    for i in range(N*N):
        if board[i]!=turn:
            continue
        row,col = to_row_col(i)
        # horizontal
        if _win_horizontal(board,row,col,turn):
            return True
        # vertical
        if _win_vertical(board,row,col,turn):
            return True
        # diag
        if _win_diag(board,row,col,turn):
            return True
        if _win_diag2(board,row,col,turn):
            return True
    return False
        
class Position(object):
    """Implementation of Gobang rules"""
    def __init__(self,board,turn,step,last):
        # board: play as A
        # turn: next player
        # step: steps until now
        # last: last move index
        self.board = board
        self.turn = turn
        self.step = step
        self.last = last
    
    def show(self):
        if self.turn=='a':
            temp_board = self.board.swapcase()
        else:
            temp_board = self.board
        print '\n'.join([temp_board[i:(i+N)] for i in range(0,N*N,N)])
    
    def move(self,index):
        # we always play as A
        if self.board[index]!='.':
            return None
        temp_board = ''.join([self.board[:index],'A',self.board[index+1:]])
        return Position(temp_board.swapcase(),self.turn.swapcase(),self.step+1,index)
    
    def moves(self):
        for i in range(N*N):
            if self.board[i]=='.':
                yield i

    def pick_move(self):
        return random.sample(list(self.moves()),1)
    
    def reward(self):
        # remember we always play as A
        if _win(self.board,'A'):
            return 1.0
        elif _win(self.board,'a'):
            return -1.0
        else:
            return 0.0
    
    def flip_vert(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[(N-1-row)*N+col] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
    
    def flip_horiz(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[N*row+(N-1-col)] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
    
    def flip_both(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[N*(N-1-row)+(N-1-col)] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
    
    def flip_clock(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[col*N+N-1-row] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
    
    def flip_reverse_clock(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[(N-1-col)*N+row] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
    
    def flip_clock2(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[col*N+row] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)

    def flip_reverse_clock2(self):
        new_board = bytearray('.'*N*N)
        for row in range(N):
            for col in range(N):
                new_board[(N-1-col)*N+N-1-row] = self.board[row*N+col]
        return Position(str(new_board),self.turn,self.step,self.last)
