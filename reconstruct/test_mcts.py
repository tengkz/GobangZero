# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 09:07:33 2018

@author: hztengkezhen
"""

from mcts import MCTS
from mcts import MCTS_player
from board import Board
from board import Game
from board import Random_player
from board import Human_player


g = Game(9)
rp = Random_player()
hp = Human_player()
mp = MCTS_player()
#num = 0
#for i in range(1):
#    if g.game_start(hp,mp)==2:
#        num+=1
#print num

board = Board(9)
board.move(4*9+4)
board.move(0*9+0)
board.move(4*9+5)
board.move(8*9+8)
board.move(4*9+6)
board.move(0*9+8)
board.move(4*9+7)
board.move(8*9+0)
board.show()

print mp.pick_move(board)