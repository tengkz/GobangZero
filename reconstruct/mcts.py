#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 00:09:11 2018

@author: ubuntu
"""

class TreeNode(object):
    def __init__(self,action):
        self.g = 0
        self.n = 0
        self.prior = 0
        self.action = action
        self.parent = None
        self.children = {}
    def expand(self,board):
        for index in board.possible_moves_set:
            self.children[index] = TreeNode(index)

class MCTS(object):
    def __init__(self):
        pass
    
    def tree_descent(self,tree,board):
        pass
    def tree_search(self,tree,board):
        leaf_node = tree_descend(tree,board)
        tree_update(leaf_node)