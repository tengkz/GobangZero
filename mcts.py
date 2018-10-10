#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 12:29:40 2018

@author: ubuntu
"""
import numpy as np
import math
import random

from net import GobangModel
from board import Position
from board import empty_board

N = 9
PRIOR_NET = 40
TEMPERATURE = 2
PRIOR_EVEN = 4
PUCT_C = 0.1
EXPAND_VISITS = 1
PROPORTIONAL_STAGE = 3
N_SIMS = 100

def encode_position(position,board_transform=None):
    my_stones,their_stones,to_play = (
            np.zeros((N,N)),np.zeros((N,N)),np.zeros((N,N))
    )
    if board_transform:
        position = eval('Position.'+board_transform)(position)
    board = position.board
    for index,char in enumerate(board):
        row,col = index//N,index%N
        if char=='A':
            my_stones[row,col]=1
        elif char=='a':
            their_stones[row,col]=1
        if position.step%2 == 1:
            to_play[row,col] = 1
    return np.stack((my_stones,their_stones,to_play),axis=-1)

class TreeNode():
    def __init__(self,net,pos):
        self.net = net
        self.pos = pos
        self.v = 0
        self.w = 0
        self.pv = 0
        self.pw = 0
        self.children = None
    
    def expand(self):
        pos_array = encode_position(self.pos)
        pos_array_new = np.expand_dims(pos_array,axis=0)
        distribution = self.net.predict_distribution(pos_array_new)
        self.children = []
        for c in self.pos.moves():
            pos2 = self.pos.move(c)
            if pos2 is None:
                continue
            node = TreeNode(self.net,pos2)
            self.children.append(node)
            value = distribution[c]
            node.pv = PRIOR_NET
            node.pw = PRIOR_NET * value
        
    def winrate(self):
        return float(self.w)/self.v if self.v>0 else float('nan')
    
    def prior(self):
        return float(self.pw)/self.pv if self.pv>0 else float('nan')
    
    def best_move(self,proportional=True):
        # choose the best move 
        if proportional:
            probs = [(float(node.v)/self.v)**TEMPERATURE for node in self.children]
            probs_tot = sum(probs)
            probs = [p/probs_tot for p in probs]
            i = np.random.choice(len(self.children),p=probs)
            return self.children[i]
        else:
            return max(self.children,key=lambda node:node.v)
    
    def distribution(self):
        distribution = np.zeros(N*N+1)
        for child in self.children:
            p = float(child.v)/self.v
            c = child.pos.last
            distribution[c] = p
        return distribution

def puct_urgency_input(nodes):
    w = np.array([float(n.w) for n in nodes])
    v = np.array([float(n.v) for n in nodes])
    pw = np.array([float(n.pw) if n.pv>0 else 1. for n in nodes])
    pv = np.array([float(n.pv) if n.pv>0 else 10. for n in nodes])
    return w,v,pw,pv

def global_puct_urgency(n0,w,v,pw,pv):
    expectation = (w+PRIOR_EVEN/2)/(v+PRIOR_EVEN)
    prior = pw/pv
    return expectation + PUCT_C*prior*math.sqrt(n0)/(1+v)

def tree_descend(tree):
    tree.v+=1
    nodes = [tree]
    root = True
    while nodes[-1].pos.reward()==0.0:
        children = list(nodes[-1].children)
        random.shuffle(children)
        urgencies = global_puct_urgency(nodes[-1].v,*puct_urgency_input(children))
        if root:
            dirichlet = np.random.dirichlet((0.03,1),len(children))
            urgencies = urgencies*0.75 + dirichlet[:,0]*0.25
            root = False
        node = max(zip(children,urgencies),key=lambda t:t[1])[0]
        nodes.append(node)
        node.v += 1
        if node.children is None:
            node.expand()
        if nodes[-1].pos.board.count('.')==0:
            break
    #print '===step number in tree descend %d' % len(nodes)
    return nodes

def tree_update(nodes,score):
    # score must be -1.0
    for node in reversed(nodes):
        node.w += score<0
        score = -score

def tree_search(tree,n_sims):
    #print 'Begin tree_search=================='
    if tree.children is None:
        tree.expand()
    i = 0
    while i<n_sims:
        nodes = tree_descend(tree)
        i+=1
        last_node = nodes[-1]
        reward = last_node.pos.reward()
        if reward!=0.0:
            score = reward
        else:
            print '============================Attention!!! reward=0 and game end!!!'
            score = tree.net.predict_winrate(np.expand_dims(encode_position(last_node.pos),axis=0))
        tree_update(nodes,score)
    
    return tree.best_move(tree.pos.step<=PROPORTIONAL_STAGE)
    #return tree.best_move()

def play_and_train(net,i,batches_per_game=2):
    positions = []
    tree = TreeNode(net=net,pos=Position(empty_board,'A',0,-1))
    tree.expand()
    while True:
        # tree search move one step
        next_tree = tree_search(tree,N_SIMS)
        positions.append((tree.pos,tree.distribution()))
        tree = next_tree
        #tree.pos.show()
        #print 'Number of A is %d, number of a is %d' % (tree.pos.board.count('A'),tree.pos.board.count('a'))
        reward = tree.pos.reward()
        if reward!=0.0:
            # attention!!!
            print 'attention reward is ',reward
            if tree.pos.turn=='A':
                score = -1.0
            else:
                score = 1.0
            #tree.expand()
            #next_tree = tree_search(tree,N_SIMS)
            #positions.append((tree.pos,tree.distribution()))
            break
        if tree.pos.step > N*N*2:
            score = 0.0
            break
        
    
    #print 'Begin fit_game=================='
    X_positions = [encode_position(pos,board_transform='flip_vert') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)
        
    X_positions = [encode_position(pos,board_transform='flip_horiz') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)

    X_positions = [encode_position(pos,board_transform='flip_both') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)
    
    X_positions = [encode_position(pos,board_transform='flip_clock') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)

    X_positions = [encode_position(pos,board_transform='flip_reverse_clock') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)

    X_positions = [encode_position(pos,board_transform='flip_clock2') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)

    X_positions = [encode_position(pos,board_transform='flip_reverse_clock2') for pos,dist in positions]
    X_dists = [dist for pos,dist in positions]
    net.fit_game(X_positions,X_dists,score)

def self_play(net):
    i=0
    win_ratio = []
    while True:
        print 'Self play for iteration %d' % i
        play_and_train(net,i)
        i+=1
        if i%5==0:
            print 'save model for game %d' % i
            net.save(i)
        # play with random player
        win_ratio.append(evaluate_random(net))
        print win_ratio
            
def evaluate_random(net):
    win_num = 0
    for j in range(100):
        pos = Position(empty_board,'A',0,-1)
        step = 0
        while True:
            pos_array = encode_position(pos)
            pos_array_new = np.expand_dims(pos_array,axis=0)
            dis = net.predict_distribution(pos_array_new)
            index = np.argmax(dis)
            while pos.board[index]!='.':
                dis[index] = 0.0
                index = np.argmax(dis)
            if pos.board[index]!='.':
                win_num+=0.5
                break
            if index == N*N:
                index = pos.pick_move()[0]
            pos = pos.move(index)
            if pos.reward()!=0:
                win_num+=1
                break
            try:
                index2 = pos.pick_move()[0]
            except Exception:
                win_num+=0.5
                break
            pos = pos.move(index2)
            if pos.reward()!=0:
                break
            step+=1
            if step>=N*N:
                win_num+=0.5
    return win_num/100.0

if __name__ == '__main__':    
    net = GobangModel(N)
    net.create()
    self_play(net)
