#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 17:12:14 2018

@author: ubuntu
"""

from mcts import encode_position,TreeNode
from board import Position,make_board,empty_board
from net import GobangModel

p0 = Position(make_board(empty_board),'a',0,-1)
p0.show()
x = encode_position(p0)
print x[10:15,0,0]
print x[10:15,0,1]
print x[10:15,0,2]

p1 = p0.move(18)
y = encode_position(p1)
print y[10:15,0,0]
print y[10:15,0,1]
print y[10:15,0,2]

p2 = p1.move(37)
z = encode_position(p2)
print z[10:15,0,0]
print z[10:15,0,1]
print z[10:15,0,2]

net = GobangModel
t0 = TreeNode(net,p0)
print list(p0.moves())

p3 = p0.move(190)
print p3