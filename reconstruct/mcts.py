#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 00:09:11 2018

@author: ubuntu
"""
import numpy as np
from operator import itemgetter

GAMMA = 0.99

class TreeNode(object):
    def __init__(self,parent,prior):
        self.parent = parent
        self.prior = prior
        self.w = 0.0
        self.n = 0.0
        self.children = {}
    
    def prefer(self,c_puct):
        """prefer in select stage"""
        u = c_puct*self.prior*np.sqrt(self.parent.n)/(1+self.n)
        if self.n>0:
            return self.w/self.n+u
        else:
            return u
    
    def update(self,score):
        """update with score"""
        self.w += score
        self.n += 1
    
    def is_leaf(self):
        return len(self.children)==0
    
    def is_root(self):
        return self.parent is None

class MCTS(object):
    def __init__(self,c_puct,tau,n_sims):
        self.c_puct = c_puct
        self.tau = tau
        self.n_sims = n_sims
        self.root = TreeNode(None,1.0)
    
    def select(self,board):
        """select a path from root to leaf"""
        node = self.root
        while not node.is_leaf():
            move_and_prefer = [(move,child.prefer(self.c_puct)) for move,child in node.children.iteritems()]
            np.random.shuffle(move_and_prefer)
            select_move = max(move_and_prefer,key=itemgetter(1))[0]
            board.move(select_move)
            node = node.children[select_move]
        return node # the leaf node to be expand
    
    def expand(self,node,board):
        """expand a node based on board state"""
        possible_moves_num = len(board.possible_moves_set)
        for move in board.possible_moves_set:
            node.children[move] = TreeNode(node,1.0/possible_moves_num)
    
    def evaluate(self,board):
        """evaluate a board state by random move"""
        current_player = board.turn
        while True:
            finish,winner = board.is_finish()
            if finish:
                if winner == current_player:
                    return 1.0
                elif winner == current_player%2+1:
                    return -1.0
                else:
                    return 0.0
            if len(board.possible_moves_set)==0:
                return 0.0
            move = np.random.choice(list(board.possible_moves_set))
            board.move(move)
        return 0.0
    
    def backup(self,leaf_node,score):
        """update backup"""
        while leaf_node:
            leaf_node.update(score)
            score = -score*GAMMA
            leaf_node = leaf_node.parent
    
    def best_move(self):
        """move from root, change root to selected child"""
        probs = [child.n**(1.0/self.tau) for child in self.root.children.values()]
        total_probs = sum(probs)
        probs = [prob/total_probs for prob in probs]
        move = np.random.choice(self.root.children.keys(),p = probs)
        self.root = self.root.children[move]
        return move
    
    def search(self,board):
        if self.root.is_leaf():
            self.expand(self.root,board)
        for i in range(self.n_sims):
            temp_board = board.copy()
            # select stage
            leaf_node = self.select(temp_board)
            finish,winner = temp_board.is_finish()
            # expand and evaluate stage
            if not finish:
                self.expand(leaf_node,temp_board)
            score = self.evaluate(temp_board)
            # backup
            self.backup(leaf_node,-score)

class MCTS_player(object):
    def __init__(self):
        self.mcts = MCTS(10.0,1.0,500)
    def pick_move(self,board):
        self.mcts.search(board)
        print [(move,child.w,child.n) for move,child in self.mcts.root.children.items()]
        return self.mcts.best_move()
    def update(self,last_move):
        if last_move in self.mcts.root.children:
            self.mcts.root = self.mcts.root.children[last_move]
        else:
            self.mcts = MCTS(10.0,1.0,500)