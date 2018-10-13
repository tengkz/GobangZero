#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 00:23:10 2018

@author: ubuntu
"""

from net import Net
network = Net(9,1,3,30000)
network.create_net()

from board import Board
b = Board(9)

result = network.policy_and_value(b)