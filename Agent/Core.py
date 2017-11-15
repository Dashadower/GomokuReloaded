# -*- coding:utf-8 -*-

import Agent.GameBoard


class BaseAI:
    """Basic class containing simple utilities for managing the GameBoard and manipulating it"""
    def __init__(self, board):
        self.Board = board
        self.Matrix = Agent.GameBoard.generate_random_matrix(self.Board.Size)

    def getopenmoves(self):
        openmoves = []
        for x in range(self.Board.Size):
            for y in range(self.Board.Size):
                if (x, y) in self.Board.Whitestones or (x, y) in self.Board.Blackstones:
                    pass
                else:
                    openmoves.append((x, y))

        return openmoves
