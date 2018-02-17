# -*- coding:utf-8 -*-
import multiprocessing
import tkinter
from tkinter.ttk import Progressbar

import GameManager, configparser

import AlphaBetaParallel
from GameBoard import GameBoard
from Interface.GomokuBoardUI import GomokuBoardUI


class MainScreen(tkinter.Frame):
    def __init__(self, master, gameboard, gridsize, buffer):
        tkinter.Frame.__init__(self, master)
        self.master = master
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.MainPane = tkinter.PanedWindow(self, orient=tkinter.HORIZONTAL)
        self.MainPane.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.GameBoardBackground = tkinter.Frame(self.MainPane)
        self.MainPane.add(self.GameBoardBackground)
        self.SideBackground = tkinter.Frame(self.MainPane)
        self.MainPane.add(self.SideBackground)
        self.GomokuBoard = GomokuBoardUI(gameboard, self.GameBoardBackground, None, gridsize, buffer)
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


def clearscreen():
    for child in root.winfo_children():
        child.destroy()


def onnewgame():

    clearscreen()

    gboard = GameBoard(int(configreader.get("GomokuBot", "BOARDSIZE_X")), int(configreader.get("GomokuBot", "BOARDSIZE_Y")))
    screen = MainScreen(root, gboard, int(configreader.get("GomokuBot", "GRIDSIZE")), int(configreader.get("GomokuBot", "BUFFER")))
    print(configreader.get("GomokuBot", "MODE"))
    if configreader.get("GomokuBot", "MODE") == "SINGLE":
        print("SINGLE")
        ai = AlphaBetaParallel.AlphaBeta(gboard,"white", int(configreader.get("GomokuBot", "DIFFICULTY")),
                                         int(configreader.get("GomokuBot", "SEARCHRANGE")))
        screen.InfoBox.config(state=tkinter.NORMAL)
        screen.InfoBox.insert(tkinter.END, "SingleProcess\n")
        screen.InfoBox.config(state=tkinter.DISABLED)

    elif configreader.get("GomokuBot", "MODE") == "MULTIPROCESS":
        print("MULTIPROCESS")
        screen.InfoBox.config(state=tkinter.NORMAL)
        screen.InfoBox.insert(tkinter.END,
                              "인공지능 설정(AlphaBetaMultiProcess):%s, %s수\n" %
                              (configreader.get("GomokuBot", "MAXPROCESSES"),
                               configreader.get("GomokuBot", "MULTIPROCESS_CUTOFF")))
        screen.InfoBox.config(state=tkinter.DISABLED)
        ai = AlphaBetaParallel.AlphaBeta(gboard, "white", int(configreader.get("GomokuBot", "DIFFICULTY")),
                                         int(configreader.get("GomokuBot", "SEARCHRANGE")))
        result = ai.initiateprocess()
        processes, pids = [result[0]], [result[1]]

        screen.InfoBox.config(state=tkinter.NORMAL)
        screen.InfoBox.insert(tkinter.END, "%s PID %s\n"%(processes, pids))
        screen.InfoBox.config(state=tkinter.DISABLED)
        
    mgr = GameManager.GameManager(root, ai, screen.GomokuBoard, screen.InfoBox, screen.progressbar, pids)
    root.protocol("WM_DELETE_WINDOW", mgr.end)
    add_menu(lambda: newgame_handler(mgr._endprocess))
    ai.ReportHook = mgr.writetotext
    screen.GomokuBoard.GameManager = mgr
    mgr.start()


def newgame_handler(killfunc):
    killfunc()
    onnewgame()


def add_menu(func):
    mainmenu = tkinter.Menu(root)
    filemenu = tkinter.Menu(mainmenu, tearoff=0)
    filemenu.add_command(label="게임하기", command=func)
    mainmenu.add_cascade(label="파일", menu=filemenu)
    root.config(menu=mainmenu)


def externmodulecall(setting_path=None):
    multiprocessing.freeze_support()
    global root, configreader
    root = tkinter.Tk()
    print(setting_path)
    configreader = configparser.RawConfigParser()
    configreader.read(setting_path)
    MainScreen(root, GameBoard(int(configreader.get("GomokuBot", "BOARDSIZE_X")), int(configreader.get("GomokuBot", "BOARDSIZE_X"))),
               int(configreader.get("GomokuBot", "GRIDSIZE")),
               int(configreader.get("GomokuBot", "BUFFER")))  # in settings.config
    add_menu(onnewgame)
    root.mainloop()


if __name__ == "__main__":
    externmodulecall()
