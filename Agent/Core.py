# -*- coding:utf-8 -*-

import Agent.GameBoard
class BaseAI:
    """Basic class contaning simple utilities for managing the GameBoard and manipulating it"""
    def __init__(self, board):
        self.Board = board
