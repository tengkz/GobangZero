# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 09:07:33 2018

@author: hztengkezhen
"""

from mcts import MCTS_player
from board import Game
from board import Random_player

rp = Random_player()
mcp = MCTS_player(10)

g = Game(9)
winner = g.self_play(mcp)
print winner