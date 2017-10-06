# -*- coding: utf-8 -*-
"""GameBoard.py: We need a uniform data structure for storing board status.
Therefore, a GameBoard class needs to be implemented"""


class GameBoard:
    def __init__(self, size):
        """Creates a GameBoard, with the board size being size tiles"""
        self.Size = size
        self.Blackstones = []
        self.Whitestones = []

    def addstone(self, position, stonetype):
        """Adds a stone to position(x,y) to the stonetype(black, white)"""
        if stonetype == "black":
            self.Blackstones.append(position)
        elif stonetype == "white":
            self.Whitestones.append(position)
