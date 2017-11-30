from Core import BaseAI
from GameBoard import GameBoard
from GeneticAnalyzerOptimized import Analyzer
from AnalyzerOptimized import WinChecker
import time, random, multiprocessing
from collections import Counter

class AlphaBeta(BaseAI):
    def __init__(self,initialgamestate,aistonetype, plydepth,tilesearchrange,analyzerparameter):
        BaseAI.__init__(self, initialgamestate, aistonetype)
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.PlyDepth = plydepth
        self.OpenSearchRange = tilesearchrange
        self.analyzerparameter = analyzerparameter


    def ChooseMove(self):
        moves = self.getlimitedopenmoves(self.Board, self.OpenSearchRange)
        startedprocesses = len(moves)
        #gboard = self.GenerateCustomGameBoard(self.Board,coord,self.AIStoneType)
        return AlphaBetaActuator(self.AIStoneType,self.PlyDepth,self.OpenSearchRange, self.analyzerparameter).CheckForWork(self.duplicateboard(self.Board))




class Node():
        def __init__(self, position, value, parent):
            self.position = position
            self.value = value
            self.parent = parent
            self.children = []
            if self.parent:
               self.parent.register_child(self)
        def register_child(self, node):
            self.children.append(node)
            node.parent = self



class AlphaBetaActuator():
    def __init__(self,aistonetype,depth,tilesearchrange, analyzerparameter):
        self.AIStoneType = aistonetype
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.PlyDepth = depth
        self.OpenSearchRange = tilesearchrange
        self.analyzer = analyzerparameter

    def CheckForWork(self,board):
            self.aiutils = BaseAI(board, self.AIStoneType)
            startnode = Node(None, None, None)
            self.AlphaBeta(self.aiutils.duplicateboard(board),startnode, self.PlyDepth, True,-10000000, 10000000, self.OpenSearchRange)
            result = []
            for items in startnode.children:
                result.append((items.value, items.position))
            result = sorted(result,key=lambda x:x[0],reverse=True)
            return result[0]
    def AlphaBeta(self,board,node,depth,isMaximizingPlayer,alpha,beta,tilesearchrange):
        #print("CURRENT POSITION",move,isMaximizingPlayer)
        if WinChecker(board).checkboth() or depth == 0:
            ganalyst = Analyzer(board, self.analyzer[0],self.analyzer[1],self.analyzer[2],self.analyzer[3])
            return ganalyst.grader(self.AIStoneType)-ganalyst.grader(self.EnemyStoneType)

        if isMaximizingPlayer:
            v = -10000000
            for moves in self.aiutils.getlimitedopenmoves(board,self.OpenSearchRange):
                g = Node(moves, None, node)
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(moves, self.AIStoneType)
                v = max(v,self.AlphaBeta(dupedboard,g,depth-1,False, alpha,beta,tilesearchrange))
                g.value = v
                alpha = max(alpha,v)
                if beta <= alpha:
                    #print("BETA CUTOFF")
                    break
            return v
        else:
            v = 10000000
            for moves in self.aiutils.getlimitedopenmoves(board,self.OpenSearchRange):
                g = Node(moves, None, node)
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(moves, self.AIStoneType)
                v = min(v,self.AlphaBeta(dupedboard,g,depth-1,True,alpha,beta,tilesearchrange))
                g.value = v
                beta = min(beta,v)
                if beta <= alpha:
                    #print("ALPHA CUTOFF")
                    break
            return v












