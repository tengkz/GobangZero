#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 01:10:52 2018

@author: ubuntu
"""

from mcts_alphazero import MCTS_selfplay
from mcts_alphazero import MCTS
from net import Net

network = Net(9,1,3,30000)
network.create_net()

mcts = MCTS(10.0,1.0,500,network)
mcts_selfplay = MCTS_selfplay(mcts)
mcts_selfplay.train()