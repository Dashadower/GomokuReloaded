# -*- coding:utf-8 -*-
"""Monte Carlo Tree Search solution for Gomoku"""

import math
from Agent.Core import BaseAI
import multiprocessing
import signal
import os
import time
import random
from queue import Empty
from Agent.AnalyzerOptimized import WinChecker

class Node:
    def __init__(self, position, gamestate, wins=0, simulations=0, parent=None):
        self.Position = position
        self.GameState = gamestate
        self.Parent = parent
        self.Children = []
        self.Wins = wins
        self.Simulations = simulations
        if self.Parent:
            self.Parent.register_child(self)

    def register_child(self, node):
        self.Children.append(node)

    def getbestchild(self):
        return sorted(self.Children, key=lambda c: c.Wins/c.Simulations + math.sqrt(math.log(self.Simulations/c.Simulations)) if c.Simulations != 0 else 0)[-1]

    def update(self, val=1):
        self.Wins += val
        self.Simulations += 1
        if self.Parent:
            self.Parent.update(val)


class MCTS(BaseAI):
    def __init__(self, initialgamestate, aistonetype, timelimit, remote=True):
        BaseAI.__init__(self, initialgamestate, aistonetype)
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.This2ActuatorQ = multiprocessing.Queue()
        self.Actuator2ThisQ = multiprocessing.Queue()
        self.TimeLimit = timelimit
        self.ReportHook = lambda x: None
        self.Process = None
        self.datalist = []
        self.PID = None

        self.Remote = remote

    def start(self):
        if self.Remote:
            return self.initiateprocess()
        else:
            self.Actuator = MCTSActuator(self.This2ActuatorQ, self.Actuator2ThisQ, self.AIStoneType, self.TimeLimit)

    def initiateprocess(self):
        p = multiprocessing.Process(target=MCTSActuator,
                                    args=(self.This2ActuatorQ, self.Actuator2ThisQ, self.AIStoneType, self.TimeLimit))
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
        self.This2ActuatorQ.put(("START", self.Board))

    def getresult(self):
        """Return data type:
        ((bestmove_eval, bestmove_position_tuple), hashtable_size)"""
        try:
            data = self.Actuator2ThisQ.get_nowait()  # ((simulation_count, position), None)
        except Empty:
            return False
        else:
            if data:
                return data
            else:
                return False


class MCTSActuator:
    def __init__(self, inputqueue, outputqueue, aistonetype, timelimit):
        self.AIStoneType = aistonetype
        self.EnemyStoneType = "black" if self.AIStoneType == "white" else "white"
        self.InputQueue = inputqueue
        self.OutputQueue = outputqueue
        self.TimeLimit = timelimit
        self.checkforwork()

    def checkforwork(self):
        while True:
            data = self.InputQueue.get()
            if data[0] == "START":
                board = data[1]
                startnode = Node(None, board)
                self.runmcts(startnode)
                best = max(startnode.Children, key=lambda x: x.Simulations)
                print("GOT", best.Position, startnode.Simulations)
                for node in startnode.Children:
                    print(node.Position, node.Simulations)
                self.OutputQueue.put(((startnode.Simulations, best.Position), None))
            elif data == "EXIT":
                break

    def run_mainloop(self, tk):
        tk.mainloop()

    def runmcts(self, startnode):
        starttime = time.time()
        node = startnode
        iters = 0

        while True:
            if time.time() - starttime > self.TimeLimit:
                break
            else:
                boardg = BaseAI(node.GameState, self.AIStoneType)
                newb = boardg.duplicateboard(node.GameState)
                while True:
                    if node.Children:
                        node = node.getbestchild()
                    else:
                        break
                if boardg.getlimitedopenmoves(node.GameState):
                    m = random.choice(boardg.getlimitedopenmoves(node.GameState))
                    newb.addstone(m, newb.Turn)
                    g = Node(m, newb, parent=node)
                    newb = boardg.duplicateboard(newb)
                    node = g
                    result = 0
                    while True:
                        if boardg.getlimitedopenmoves(newb):
                            newb.addstone(random.choice(boardg.getlimitedopenmoves(newb)), newb.Turn)
                            check = WinChecker(newb)
                            if check.check(self.AIStoneType):
                                result = 1
                                break
                            elif check.check(self.EnemyStoneType):
                                result = -1
                                break
                            else:
                                break

                        else:
                            break
                    node.update(result)
            iters += 1
        print("iters", iters)
        return 0


def uct(wi, si, n, nj, c=math.sqrt(2)):
    """Upper Confidence bound for Trees
    wi: number of wins
    si: number of simulations
    n: number of visits
    nj: number of visits for parent node
    c: exploration parameter
"""
    return wi/si + c * math.sqrt(math.log(nj)/n) if n else 0
