from Agent.Core import BaseAI
from Agent.AnalyzerOptimized import Analyzer, WinChecker, ExtensiveAnalysis
import multiprocessing
import signal
import os
from queue import Empty
from Agent.GameBoard import generate_random_matrix


class AlphaBeta(BaseAI):
    def __init__(self, initialgamestate, aistonetype, plydepth, tilesearchrange, use_xta, xta_coefficient, remote = True):
        BaseAI.__init__(self, initialgamestate, aistonetype)
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.PlyDepth = plydepth
        self.This2ActuatorQ = multiprocessing.Queue()
        self.Actuator2ThisQ = multiprocessing.Queue()
        self.OpenSearchRange = tilesearchrange

        self.ReportHook = lambda x: None
        self.Process = None
        self.datalist = []
        self.PID = None
        self.Use_XTA = True if use_xta else False
        self.XTA_Coefficient = xta_coefficient

        self.Remote = remote

    def startalphabeta(self):
        if self.Remote:
            return self.initiateprocess()
        else:
            self.Actuator = AlphaBetaActuator(self.This2ActuatorQ, self.Actuator2ThisQ, self.AIStoneType, self.PlyDepth,
                                              self.OpenSearchRange, self.Use_XTA, self.XTA_Coefficient)
    def initiateprocess(self):
        p = multiprocessing.Process(target=AlphaBetaActuator,
                                    args=(self.This2ActuatorQ, self.Actuator2ThisQ, self.AIStoneType,
                                          self.PlyDepth, self.OpenSearchRange, self.Use_XTA, self.XTA_Coefficient))
        p.daemon = True
        self.Process = p
        p.start()
        self.PID = p.pid

        return self.Process, self.PID

    def killprocess(self):
        self.This2ActuatorQ.put("EXIT")
        if self.PID:
            os.kill(self.PID, signal.SIGTERM)
    def choosemove(self):
        moves = self.getlimitedopenmoves(self.Board, self.OpenSearchRange)
        searchtiles = len(moves)
        self.ReportHook("1PLY Search tiles:"+str(searchtiles))
        self.This2ActuatorQ.put(("START", self.Board))

    def getresult(self):
        """Return data type:
        ((bestmove_eval, bestmove_position_tuple), hashtable_size)"""
        try:
            data = self.Actuator2ThisQ.get_nowait()
        except Empty:
            return False
        else:
            if data:
                if not self.Remote:
                    self.killprocess()
                return data
            else:
                return False


class Node:
        def __init__(self, position, value, parent, alpha, beta):
            self.position = position
            self.value = value
            self.parent = parent
            self.children = []
            self.alpha = alpha
            self.beta = beta
            if self.parent:
                self.parent.register_child(self)

        def register_child(self, node):
            self.children.append(node)
            node.parent = self


class AlphaBetaActuator:
    def __init__(self, inputqueue, outputqueue, aistonetype, depth, tilesearchrange, use_xta, xta_coefficient):
        self.AIStoneType = aistonetype
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.InputQueue = inputqueue
        self.OutputQueue = outputqueue
        self.PlyDepth = depth
        self.OpenSearchRange = tilesearchrange
        self.aiutils = None
        self.Matrix = generate_random_matrix(25)  # Select default Zobrist matrix size as 25, change if necessary
        self.Zobrist_Hash_Table = []  # Moved the below 2 lines of code up to __init__ to avoid PEP warnings
        self.CurrentDepth = 1
        self.Iterations = 0
        self.TerminalNodes = 0
        self.Use_XTA = True if use_xta else False
        self.XTA_Coefficient = xta_coefficient
        self.checkforwork()

    def checkforwork(self):
        while True:
            data = self.InputQueue.get()
            if data[0] == "START":
                board = data[1]

                self.aiutils = BaseAI(board, self.AIStoneType)
                hashtable_size = []
                #print("*" * 10)
                self.Zobrist_Hash_Table = []
                for depth in range(1, self.PlyDepth+1):
                    self.TerminalNodes = 0
                    startnode = Node(None, None, None, -10000000, 10000000)
                    self.alphabeta(self.aiutils.duplicateboard(board), startnode, depth, True,
                                   self.OpenSearchRange, self.CurrentDepth)
                    self.CurrentDepth += 1
                    #print("DEPTH", depth, "HASH SIZE:", len(self.Zobrist_Hash_Table))
                    hashtable_size.append(len(self.Zobrist_Hash_Table))

                best = max(startnode.children, key=lambda x: x.value)
                #print("RESULT:", best.position, best.value, "ITERATIONS:", self.Iterations, "TERMINAL_NODES:", self.TerminalNodes)
                self.OutputQueue.put(((best.value, best.position), hashtable_size))
            elif data == "EXIT":
                break

    def alphabeta(self, board, node, depth, ismaximizingplayer, tilesearchrange, originaldepth):
        self.Iterations += 1
        # Hash table is disabled for now until I'm sure it helps with performance
        """hashval = board.generatehash(self.Matrix)
        for hash in self.Zobrist_Hash_Table:
            if hash[0] == hashval:
                if hash[2] < originaldepth - 1:
                    self.Zobrist_Hash_Table.remove(hash)
                else:
                    return hash[1]"""
        # print("CURRENT POSITION",move,isMaximizingPlayer)
        if WinChecker(board).checkboth() or depth == 0:
            """hashval = board.generatehash(self.Matrix)
            for hash in self.Zobrist_Hash_Table:
                if hash[0] == hashval:
                    if hash[2] < originaldepth-1:
                        self.Zobrist_Hash_Table.remove(hash)
                    else:
                        return hash[1]"""
            ganalyst = Analyzer(board)
            aiscore = ganalyst.grader(self.AIStoneType)
            enemyscore = ganalyst.grader(self.EnemyStoneType)
            if self.Use_XTA:
                coefficient = ExtensiveAnalysis(board).grader(self.AIStoneType)
                # Hash table is disabled for now until I'm sure it helps with performance
                # self.Zobrist_Hash_Table.append((hashval, aiscore - enemyscore - (self.XTA_Coefficient*coefficient), originaldepth))
                return aiscore - enemyscore - (self.XTA_Coefficient*coefficient)

            else:
                # Hash table is disabled for now until I'm sure it helps with performance
                #self.Zobrist_Hash_Table.append((hashval, aiscore - enemyscore, originaldepth))
                return aiscore - enemyscore
        if ismaximizingplayer:
            v = -10000000
            for move in self.aiutils.getlimitedopenmoves(board, self.OpenSearchRange):
                g = Node(move, None, node, node.alpha, node.beta)
                if depth == 1: self.TerminalNodes += 1
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(move, self.AIStoneType)
                v = max(v, self.alphabeta(dupedboard, g, depth-1, False, tilesearchrange, originaldepth))
                g.value = v
                node.alpha = max(node.alpha, v)
                if node.beta <= node.alpha:
                    break
            return v
        else:
            v = 10000000
            for move in self.aiutils.getlimitedopenmoves(board, self.OpenSearchRange):
                g = Node(move, None, node, node.alpha, node.beta)
                if depth == 1: self.TerminalNodes += 1
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(move, self.EnemyStoneType)
                v = min(v, self.alphabeta(dupedboard, g, depth-1, True, tilesearchrange, originaldepth))
                g.value = v
                node.beta = min(node.beta, v)
                if node.beta <= node.alpha:
                    break
            return v
