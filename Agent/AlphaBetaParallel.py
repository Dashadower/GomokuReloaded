from Core import BaseAI
from AnalyzerOptimized import Analyzer, WinChecker
import multiprocessing
from queue import Empty
from GameBoard import generate_random_matrix

class AlphaBeta(BaseAI):
    def __init__(self, initialgamestate, aistonetype, plydepth, tilesearchrange):
        BaseAI.__init__(self, initialgamestate, aistonetype)
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.PlyDepth = plydepth
        self.This2ActuatorQ = multiprocessing.Queue()
        self.Actuator2ThisQ = multiprocessing.Queue()
        self.OpenSearchRange = tilesearchrange

        self.ReportHook = print
        self.Process = None
        self.datalist = []
        self.PID = None

    def initiateprocess(self):
        p = multiprocessing.Process(target=AlphaBetaActuator,
                                    args=(self.This2ActuatorQ, self.Actuator2ThisQ, self.AIStoneType,
                                          self.PlyDepth, self.OpenSearchRange))
        p.daemon = True
        self.Process = p
        p.start()
        self.PID = p.pid

        return self.Process, self.PID

    def choosemove(self):
        moves = self.getlimitedopenmoves(self.Board, self.OpenSearchRange)
        searchtiles = len(moves)
        self.ReportHook("1PLY 검색 타일 수:"+str(searchtiles))
        self.This2ActuatorQ.put(("START", self.Board))

    def getresult(self):
        try:
            data = self.Actuator2ThisQ.get_nowait()
        except Empty:
            return False
        else:
            if data:
                return data
            else:
                return False


class Node:
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


class AlphaBetaActuator:
    def __init__(self, inputqueue, outputqueue, aistonetype, depth, tilesearchrange):
        self.AIStoneType = aistonetype
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.InputQueue = inputqueue
        self.OutputQueue = outputqueue
        self.PlyDepth = depth
        self.OpenSearchRange = tilesearchrange
        self.checkforwork()
        self.aiutils = None

    def checkforwork(self):
        while True:
            data = self.InputQueue.get()
            if data[0] == "START":
                board = data[1]
                self.Matrix = generate_random_matrix(board.Size[0])
                self.Zobrist_Hash_Table = []
                self.CurrentDepth = 1
                self.aiutils = BaseAI(board, self.AIStoneType)
                hashtable_size = []
                for depth in range(1, self.PlyDepth+1):
                    startnode = Node(None, None, None)
                    self.alphabeta(self.aiutils.duplicateboard(board), startnode, depth, True, -10000000, 10000000,
                                   self.OpenSearchRange, self.CurrentDepth)
                    self.CurrentDepth += 1
                    print("DEPTH", depth, "HASH SIZE:", len(self.Zobrist_Hash_Table))
                    hashtable_size.append(len(self.Zobrist_Hash_Table))
                print("*"*10)
                print(len(startnode.children))
                result = []
                for items in startnode.children:
                    print(items.position, items.value)
                    result.append((items.value, items.position))
                result = sorted(result, key=lambda x: x[0], reverse=True)
                print("RESULT:", result)
                self.OutputQueue.put((result[0],hashtable_size))

    def alphabeta(self, board, node, depth, ismaximizingplayer, alpha, beta, tilesearchrange, originaldepth):
        hashval = board.generatehash(self.Matrix)
        for hash in self.Zobrist_Hash_Table:
            if hash[0] == hashval:
                if hash[2] < originaldepth - 1:
                    self.Zobrist_Hash_Table.remove(hash)
                else:
                    return hash[1]
        # print("CURRENT POSITION",move,isMaximizingPlayer)
        if WinChecker(board).checkboth() or depth == 0:
            hashval = board.generatehash(self.Matrix)
            for hash in self.Zobrist_Hash_Table:
                if hash[0] == hashval:
                    if hash[2] < originaldepth-1:
                        self.Zobrist_Hash_Table.remove(hash)
                    else:
                        return hash[1]
            ganalyst = Analyzer(board)
            # aiscore = ganalyst.grader(self.AIStoneType if ismaximizingplayer else self.EnemyStoneType)
            aiscore = ganalyst.grader(self.AIStoneType)
            # enemyscore = ganalyst.grader(self.EnemyStoneType if ismaximizingplayer else self.AIStoneType)
            enemyscore = ganalyst.grader(self.EnemyStoneType)
            self.Zobrist_Hash_Table.append((hashval, aiscore-enemyscore, originaldepth))
            return aiscore-enemyscore

        if ismaximizingplayer:
            v = -10000000
            for move in self.aiutils.getlimitedopenmoves(board, self.OpenSearchRange):
                g = Node(move, None, node)
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(move, self.AIStoneType)
                v = max(v, self.alphabeta(dupedboard, g, depth-1, False, alpha, beta, tilesearchrange, originaldepth))
                g.value = v
                alpha = max(alpha, v)
                if beta <= alpha:
                    # print("BETA CUTOFF")
                    break
            return v
        else:
            v = 10000000
            for move in self.aiutils.getlimitedopenmoves(board, self.OpenSearchRange):
                g = Node(move, None, node)
                dupedboard = self.aiutils.duplicateboard(board)
                dupedboard.addstone(move, self.EnemyStoneType)
                v = min(v, self.alphabeta(dupedboard, g, depth-1, True, alpha, beta, tilesearchrange, originaldepth))
                g.value = v
                beta = min(beta, v)
                if beta <= alpha:
                    # print("ALPHA CUTOFF")
                    break
            return v
