#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 23:14:41 2018

@author: ubuntu
"""

from board import Board
from board import Game
from board import Random_player

g = Game(9)
num = 0
for i in range(100):
    w = g.self_play(Random_player())
    if w==1:
        num+=1
print num