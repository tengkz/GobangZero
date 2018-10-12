#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 00:09:11 2018

@author: ubuntu
"""
import numpy as np

class TreeNode(object):
    def __init__(self,action):
        self.g = 0.0
        self.n = 0.0
        self.prior = 0.0
        self.action = action
        self.parent = None
        self.children = {}
        self.player = 0
    
    def expand(self,board):
        possible_moves_num = len(board.possible_moves_set)
        for index in board.possible_moves_set:
            self.children[index] = TreeNode(index)
            self.children[index].prior = 1.0/possible_moves_num
            self.children[index].parent = self
            self.children[index].player = board.turn
    
    def pick(self):
        probs = [child.prior for child in self.children.values()]
        probs_total = sum(probs)
        real_probs = [prob/probs_total for prob in probs]
        if sum(probs)<0.5:
            print probs
            
        return np.random.choice(self.children.values(),p=real_probs)
    
    def best_move(self):
        action_list = self.children.keys()
        value_list = [child.g/child.n if child.n>0 else 0.0 for child in self.children.values()]
        return max(zip(action_list,value_list),key=lambda t:t[1])[0]

class MCTS(object):
    def __init__(self,sim_num):
        self.sim_num = sim_num
    
    def tree_descent(self,tree,board):
        temp_board = board.copy()
        temp_tree = tree
        while True:
            if len(temp_tree.children)==0:
                temp_tree.expand(temp_board)
            temp_move = temp_tree.pick()
            temp_board.move(temp_move.action)
            temp_tree = temp_tree.children[temp_move.action]
            finish,winner = temp_board.is_finish()
            if finish:
                return temp_tree,winner
    
    def tree_ascent(self,leaf_node,winner,root):
        while leaf_node!=root:
            leaf_node.n += 1
            leaf_node.g += 1 if leaf_node.player == winner else 0
            leaf_node = leaf_node.parent
            
    def tree_search(self,tree,board):
        for i in range(self.sim_num):
            leaf_node,winner = self.tree_descent(tree,board)
            self.tree_ascent(leaf_node,winner,tree)
        return tree.best_move()

class MCTS_player(MCTS):
    def __init__(self,sim_num):
        super(MCTS_player,self).__init__(sim_num)
    def pick_move(self,board):
        tree = TreeNode(-1)
        return self.tree_search(tree,board)