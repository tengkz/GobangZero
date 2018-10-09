#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 16:56:36 2018

@author: ubuntu
"""

from board import make_board,Position,empty_board

p0 = Position(empty_board,'A',0,-1)
p0.show()
print '==========='
p1 = p0.move(0)
p1.show()
print '==========='
p2 = p1.move(1)
p2.show()
print '==========='
p3 = p2.move(2)
p3.show()
print '==========='
board = make_board(empty_board)
p4 = Position(board,'A',10,-1)
p4.show()
p5 = p4.flip_clock()
print '==========='
p5.show()
print '==========='
p6 = p4.flip_reverse_clock()
p6.show()