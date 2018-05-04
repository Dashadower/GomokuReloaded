# -*- coding:utf-8 -*-
import tkinter
from tkinter.ttk import Progressbar
from tkinter.messagebox import showerror
from tkinter.simpledialog import askinteger
import Interface.GameManager
import sys
from ConfigReader import ConfigReader
import Agent.AlphaBetaParallel
import Agent.MonteCarlo
from Agent.GameBoard import GameBoard
from Interface.GomokuBoardUI import GomokuBoardUI
import constants


class MainScreen(tkinter.Frame):
    def __init__(self, master, gameboard, config_reader):
        if not gameboard:
            return
        tkinter.Frame.__init__(self, master)
        self.master = master
        self.ConfigReader = config_reader
        self.GridSize = self.ConfigReader.retrieve("GRIDSIZE")
        self.BoardBuffer = self.ConfigReader.retrieve("BUFFER")

        self.GameBoard = gameboard

        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.draw()

    def draw(self):
        self.MainPane = tkinter.PanedWindow(self, orient=tkinter.HORIZONTAL)
        self.MainPane.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        self.GameBoardBackground = tkinter.Frame(self.MainPane)
        self.MainPane.add(self.GameBoardBackground)
        self.SideBackground = tkinter.Frame(self.MainPane)
        self.MainPane.add(self.SideBackground)

        self.GomokuBoard = GomokuBoardUI(self.GameBoard, self.GameBoardBackground, None, self.GridSize, self.BoardBuffer)

        self.TextFrame = tkinter.Frame(self.SideBackground)
        self.TextFrame.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        self.scrollbar = tkinter.Scrollbar(self.TextFrame)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.InfoBox = tkinter.Text(self.TextFrame)
        self.InfoBox.pack(side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.BOTH)
        self.InfoBox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.InfoBox.yview)
        self.InfoBox.insert(tkinter.END, "GomokuBot\n")
        self.InfoBox.config(state=tkinter.DISABLED)

        self.progressbar = Progressbar(self.SideBackground, mode="indeterminate")
        self.progressbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.add_menu()

    def clearscreen(self):
        """Clears all widgets within class Frame"""
        for child in self.winfo_children():
            child.destroy()

    def add_menu(self):
        """Adds menu items to master(must be root)"""
        self.mainmenu = tkinter.Menu(root)
        self.filemenu = tkinter.Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label="Play a game", command=self.onnewgame)
        self.filemenu.add_command(label="Exit", command=sys.exit)
        self.mainmenu.add_cascade(label="File", menu=self.filemenu)
        self.master.config(menu=self.mainmenu)

    def displaymesage(self, text):
        self.InfoBox.config(state=tkinter.NORMAL)
        self.InfoBox.insert(tkinter.END, str(text)+"\n")
        self.InfoBox.config(state=tkinter.DISABLED)

    def onnewgame(self):
        board_size = askinteger(constants.Master_Dialog_Title, "Enter the board's size", initialvalue=15)
        self.GameBoard = GameBoard(board_size, board_size)
        if self.ConfigReader.retrieve("AIMODE") == "ALPHABETA":
            ai = Agent.AlphaBetaParallel.AlphaBeta(self.GameBoard, "white", self.ConfigReader.retrieve("DIFFICULTY"),
                                                   self.ConfigReader.retrieve("SEARCHRANGE"),
                                                   self.ConfigReader.retrieve("USE_EXTENSIVE_ANALYSIS"),
                                                   self.ConfigReader.retrieve("EA_COEFFICIENT"))
        elif self.ConfigReader.retrieve("AIMODE") == "MCTS":
            ai = Agent.MonteCarlo.MCTS(self.GameBoard, "white", self.ConfigReader.retrieve("TIMELIMIT"))
        else:
            showerror(constants.Master_Dialog_Title, "Invalid AI startup invoked! Please check settings")
            self.master.destroy()
            sys.exit(1)
        process, pid = ai.start()
        self.displaymesage("Worker pid: %d"%(pid))
        self.GomokuBoard.GameBoard = self.GameBoard
        mgr = Interface.GameManager.GameManager(root, ai, self.GomokuBoard, self.InfoBox, self.progressbar, [pid],
                                                self.ConfigReader.retrieve("AIMODE"))
        root.protocol("WM_DELETE_WINDOW", mgr.end)
        ai.ReportHook = mgr.writetotext
        self.GomokuBoard.GameManager = mgr
        mgr.start()


def externmodulecall(setting_path="../settings.config"):
    global root, configreader
    root = tkinter.Tk()
    configreader = ConfigReader(setting_path)
    MainScreen(root, GameBoard(configreader.retrieve("BOARDSIZE_X"), configreader.retrieve("BOARDSIZE_Y")), configreader)  # in settings.config
    root.mainloop()


if __name__ == "__main__":
    externmodulecall()
