# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 15:42:05 2018

@author: hztengkezhen
"""
import random

N = 4
empty_board = '.'*N*N
PRIOR_EVEN = 4

class Position(object):
    def __init__(self,board,turn,step,last):
        self.board = board
        self.turn = turn
        self.step = step
        self.last = last
        self.reward = 0.0
        if self.step>=16:
            A_cnt = self.board.count('A')
            a_cnt = self.board.count('a')
            if A_cnt>a_cnt:
                self.reward = 1.0
            elif A_cnt==a_cnt:
                self.reward = 0.0
            else:
                self.reward = -1.0

    def show(self):
        if self.turn=='a':
            temp_board = self.board.swapcase()
        else:
            temp_board = self.board
        print '\n'.join([temp_board[i:(i+N)] for i in range(0,N*N,N)])
    
    def move(self,index):
        if self.board[index]=='A':
            return None
        temp_board = ''.join([self.board[:index],'A',self.board[index+1:]])
        return Position(temp_board.swapcase(),self.turn.swapcase(),self.step+1,index)
    
    def moves(self):
        for i in range(N*N):
            if self.board[i]!='A':
                yield i
    
    def pick_move(self):
        return random.sample(list(self.moves()),1)

class TreeNode():
    def __init__(self,pos):
        self.pos = pos
        self.v = 0.0
        self.w = 0.0
        self.children = None
    
    def expand(self):
        self.children = []
        for c in self.pos.moves():
            pos2 = self.pos.move(c)
            if pos2 is None:
                continue
            node = TreeNode(pos2)
            self.children.append(node)
    
    def best_move(self):
        return max(self.children,key=lambda node:node.v)

def tree_descend(tree):
    print 'begin tree descend'
    tree.v += 1
    nodes = [tree]
    while nodes[-1].pos.step<16:
        children = list(nodes[-1].children)
        random.shuffle(children)
        emergency = [(item.w+PRIOR_EVEN/2)/(item.v+PRIOR_EVEN) for item in children]
        node = max(zip(children,emergency),key=lambda t:t[1])[0]
        nodes.append(node)
        node.v += 1
        if node.children is None:
            node.expand()
    return nodes

def tree_update(nodes,score):
    for node in reversed(nodes):
        node.w += score<0
        score = -score

def tree_search(tree):
    if tree.children is None:
        tree.expand()
    i = 0
    while i<100:
        print 'tree search sim %d' % i
        nodes = tree_descend(tree)
        i+=1
        last_node = nodes[-1]
        score = last_node.pos.reward
        print 'score=',score
        tree_update(nodes,score)
    print [(item.w,item.v) for item in tree.children]
    return tree.best_move()

def self_play():
    positions = []
    tree = TreeNode(Position(empty_board,'A',0,-1))
    tree.expand()
    while True:
        next_tree = tree_search(tree)
        positions.append(tree.pos)
        tree = next_tree
        reward = tree.pos.reward
        if reward!=0.0:
            break
    return positions

if __name__ == '__main__':
    p = self_play()
    for item in p:
        item.show()
        print '=========='