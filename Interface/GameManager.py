
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
        self.writetotext("검색 깊이: "+str(self.AI.PlyDepth)+" 수(PLY) 검색 범위: "+str(self.AI.OpenSearchRange)+"칸(TILE)")
        tkinter.messagebox.showinfo("", "플레이어의 차례입니다")
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
            tkinter.messagebox.showinfo("", "컴퓨터의 승리입니다")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("AI WIN")
            self.writetotext("총 게임시간(입출력 시간 포함):" + str(time.time() - self.StartTime))
            return True
        elif self.refree.check(self.PlayerStoneType):
            tkinter.messagebox.showinfo("", "인간의 승리입니다.")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("USER WIN")
            self.writetotext("총 게임시간(입출력 시간 포함):" + str(time.time() - self.StartTime))
            return True
        elif not self.AI.getopenmoves():
            tkinter.messagebox.showinfo("", "무승부 입니다")
            self.GomokuBoard.PlayerTurn = False
            self.writetotext("DRAW")
            self.writetotext("총 게임시간(입출력 시간 포함):" + str(time.time() - self.StartTime))
        else:
            return False

    def registeruserstone(self, coords):
        self.AI.addopponentstone(coords)
        self.writetotext("Human stone"+str(coords))
        self.GomokuBoard.PlayerTurn = False
        if not self.checkwin():
            self.progressbar.start()
            self.writetotext("인공지능의 차례입니다.")
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
            self.writetotext("평가함수 결과(Grader()):"+str(data[0][0])+" 위치:"+str(data[0][1]))
            self.AI.addaistone(data[0][1])
            if data[0][0] >= 9900000:

                self.writetotext("인공지능의 필승입니다 ^^")
            self.writetotext("계산시간(입출력 시간 포함):" + str(time.time() - self.CalcTime))
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
