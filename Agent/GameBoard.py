# -*- coding: utf-8 -*-
"""GameBoard.py: We need a uniform data structure for storing board status.
Therefore, a GameBoard class needs to be implemented"""

import random


def random_number():
    return random.randint(1, 99999)


def generate_random_matrix(boardsize):
    randoms = []
    for x in range(0, boardsize):
        randoms.append([])
        for y in range(0, boardsize):

            rarr = [random_number(), random_number(), random_number()]
            randoms[x].append(rarr)
    randoms.insert(len(randoms), [random_number(), random_number()])
    return randoms


class GameBoard:
    def __init__(self, size_x, size_y):
        """Creates a GameBoard, with the board size being size tiles"""
        self.Size = (size_x, size_y)
        self.BlackStones = []
        self.WhiteStones = []
        self.Turn = "black"  # Note: Turn states the color who needs to PUT NEXT, not the color that last placed a stone

    def addstone(self, position, stonetype):
        """Adds a stone to position(x,y) to the stonetype(black, white)"""
        if stonetype == "black":
            self.BlackStones.append(position)
            self.Turn = "white"

        elif stonetype == "white":
            self.WhiteStones.append(position)
            self.Turn = "black"

    def generatehash(self, matrix):
        board_hash = 0
        for x in range(1, self.Size[0] + 1):
            for y in range(1, self.Size[1] + 1):
                if (x, y) in self.BlackStones:
                    piece = 1
                elif (x, y) in self.WhiteStones:
                    piece = 2
                else:
                    piece = 0
                board_hash ^= matrix[x - 1][y - 1][piece]
        if self.Turn == "black":
            board_hash ^= matrix[len(matrix) - 1][0]
        elif self.Turn == "white":
            board_hash ^= matrix[len(matrix) - 1][1]
        return board_hash
