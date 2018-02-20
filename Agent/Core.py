# -*- coding:utf-8 -*-

import Agent.GameBoard


class BaseAI:
    """Basic class containing simple utilities for managing the GameBoard and manipulating it"""
    def __init__(self, board, aistonetype):
        self.Board = board
        self.AIStoneType = aistonetype
        self.Matrix = Agent.GameBoard.generate_random_matrix(self.Board.Size[0])

    def getopenmoves(self):
        openmoves = []
        for x in range(1, self.Board.Size[0]+1):
            for y in range(1, self.Board.Size[1]+1):
                if (x, y) in self.Board.WhiteStones or (x, y) in self.Board.BlackStones:
                    pass
                else:
                    openmoves.append((x, y))

        return openmoves

    def getlimitedopenmoves(self, board, searchrange=1):
        """Returns available unoccupied positions  within a square of the outermost stones + range
        Used to reduce number of simulations"""
        openmoves = []

        for stones in board.BlackStones + board.WhiteStones:
            for x, y in [(stones[0] + i, stones[1] + j) for i in range(-searchrange, searchrange+1) for j in range(-searchrange, searchrange+1) if i != 0 or j != 0]:
                if x > board.Size[0] or x <= 0 or y > board.Size[1] or y <= 0:
                    pass
                else:
                    if (x, y) not in board.WhiteStones+board.BlackStones:
                        openmoves.append((x, y))
        setted = set(openmoves)
        return list(setted)

    def addaistone(self, position):
        self.Board.addstone(position, self.AIStoneType)

    def addopponentstone(self, position):
        self.Board.addstone(position, "white" if self.AIStoneType == "black" else "black")

    def duplicateboard(self, board):
        g = Agent.GameBoard.GameBoard(board.Size[0], board.Size[1])
        for bstone in board.BlackStones:
            g.addstone(bstone, "black")

        for wstone in board.WhiteStones:
            g.addstone(wstone, "white")
        if len(g.BlackStones) == len(g.WhiteStones):
            g.Turn = "black"
        else:
            g.Turn = "white"
        return g


if __name__ == "__main__":
    b = Agent.GameBoard.GameBoard(15,15)
    b.addstone((3, 5), "black")
    b.addstone((3, 6), "black")
    g = BaseAI(b, "black")
    print(g.getlimitedopenmoves(b))
