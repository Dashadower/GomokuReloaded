
import Agent.AnalyzerOptimized
import tkinter
import time
import os
import signal
import sys
import tkinter.messagebox


class GameManager:
    def __init__(self, mainui, aiobject, gboard, textfield, progressbar, pids):
        self.MainUI = mainui
        self.TextField = textfield
        self.progressbar = progressbar
        self.pids = pids
        self.GomokuBoard = gboard
        self.AI = aiobject
        self.AIStoneType = self.AI.AIStoneType
        self.PlayerStoneType = "black" if self.AIStoneType == "white" else "white"
        self.refree = Agent.AnalyzerOptimized.WinChecker(self.AI.Board)
        self.StartTime = None
        self.CalcTime = None

    def start(self):
        self.writetotext("Search depth: "+str(self.AI.PlyDepth)+" Depth(PLY) Search Range: "+str(self.AI.OpenSearchRange)+"tiles")
        tkinter.messagebox.showinfo("", "Player's turn")
        self.GomokuBoard.PlayerTurn = True
        self.StartTime = time.time()

    def end(self):
        if self.pids:
            for pid in self.pids:
                os.kill(pid, signal.SIGTERM)
            sys.exit()
        else:
            sys.exit()

    def _endprocess(self):
        if self.pids:
            for pid in self.pids:
                os.kill(pid, signal.SIGTERM)

    def checkwin(self):
        if self.refree.check(self.AIStoneType):
            tkinter.messagebox.showinfo("", "Computer Wins")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("Computer wins.")
            self.writetotext("Total game time(including input/output):" + str(time.time() - self.StartTime))
            return True
        elif self.refree.check(self.PlayerStoneType):
            tkinter.messagebox.showinfo("", "Player Wins.")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("Player wins.")
            self.writetotext("Total game time(including input/output):" + str(time.time() - self.StartTime))
            return True
        elif not self.AI.getopenmoves():
            tkinter.messagebox.showinfo("", "It's a Draw")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("DRAW")
            self.writetotext("Total game time(including input/output):" + str(time.time() - self.StartTime))
        else:
            return False

    def registeruserstone(self, coords):
        self.AI.addopponentstone(coords)
        self.writetotext("Human stone"+str(coords))
        self.GomokuBoard.PlayerTurn = False
        if not self.checkwin():
            self.progressbar.start()
            self.writetotext("Computer's turn.")
            self.chooseaimove()

    def chooseaimove(self):
        self.CalcTime = time.time()

        self.AI.choosemove()
        self.MainUI.after(200, self.waitforinput)

    def waitforinput(self):
        data = self.AI.getresult()

        if not data:
            self.MainUI.after(200, self.waitforinput)
            # self.Writetotext(str(data)+str(self.AI.ControlQueue.empty()))
        else:
            self.writetotext("AI Move Recieved")
            self.progressbar.stop()
            x = 1
            for item in data[1]:
                self.writetotext("Depth %d hashtable size: %d"%(x, item))
                x += 1
            self.writetotext("Evaluation Function value(Grader()):"+str(data[0][0])+" 위치:"+str(data[0][1]))
            self.AI.addaistone(data[0][1])
            if data[0][0] >= 9900000:

                self.writetotext("Computer is to win for certain ^^")
            self.writetotext("Total game time(including input/output):" + str(time.time() - self.CalcTime))
            self.GomokuBoard.clear()
            self.GomokuBoard.draw()
            self.MainUI.update()
            if not self.checkwin():
                # tkinter.messagebox.showinfo("","플레이어의 차례입니다")
                self.GomokuBoard.PlayerTurn = True

    def writetotext(self, text):
        self.TextField.config(state="normal")
        self.TextField.insert("end", str(text)+"\n")
        self.TextField.see("end")
        self.TextField.config(state="disabled")
