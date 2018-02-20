import argparse
import sys
import multiprocessing
import os
import configparser
from Agent.AlphaBetaParallel import AlphaBeta
from Agent.GameBoard import GameBoard
from Interface.GomokuUI import externmodulecall

helpmsg = """Console commands for GomokuBot:
boardsize x y             Override the config file and sets the board size to x, y
start                     Starts a game with the Player playing black(first)
placestone x y            Place a player stone at position x y
cpuplay                   Makes the Computer return a move
stoneinfo                 Returns a list of black stones on one line, and white stones on the next line
endgame                   Terminates an existing game
exit                      Exits GomokuBot
Note that commands cannot be run on the computer's turn if MODE is set to singleprocess
"""

class InputHandler:
    def __init__(self, cmdargv, configpath):
        self.cmdargv = vars(cmdargv)
        self.DebugMode = self.cmdargv["debug"]
        self.MCTSMode = self.cmdargv["mcts"]
        self.HideConsole = self.cmdargv["noconsole"]
        self.HideGUI = self.cmdargv["nogui"]
        self.AI = None
        self.GameBoard = None
        self.Turn = "player"
        self.ConfigReader = configparser.RawConfigParser()
        self.ConfigReader.read(configpath)

        self.BoardSize_X = int(self.ConfigReader.get("GomokuBot", "BoardSize_X"))
        self.BoardSize_Y = int(self.ConfigReader.get("GomokuBot", "BoardSize_Y"))
        self.Difficulty = int(self.ConfigReader.get("GomokuBot", "DIFFICULTY"))
        self.TileSearchRange = int(self.ConfigReader.get("GomokuBot", "SEARCHRANGE"))
        self.RunRemote = True if self.ConfigReader.get("GomokuBot", "MODE") == "MULTIPROCESS" else False
        self.Use_XTA = True if self.ConfigReader.get("GomokuBot", "USE_EXTENSIVE_ANALYSIS") == "1" else False
        self.XTA_Coefficient = float(self.ConfigReader.get("GomokuBot", "EA_COEFFICIENT"))

        if self.cmdargv["stdcomm"]:
            self.IOMethod = "STDIO"
        elif self.cmdargv["silent"]:
            self.IOMethod = "SOCKET"
            self.socket_addr = self.cmdargv["socket"][0]
            self.socket_port = self.cmdargv["socket"][1]

        self.runlistener()

    def runlistener(self):
        while True:
            inputcmd = input()
            if inputcmd == "help":
                print(helpmsg)
            elif inputcmd == "exit":
                if self.AI:
                    self.AI.killprocess()
                sys.exit(0)
            elif inputcmd == "start":
                self.GameBoard = GameBoard(self.BoardSize_X, self.BoardSize_Y)
                if self.AI and self.RunRemote:
                    self.AI.killprocess()
                self.AI = AlphaBeta(self.GameBoard, "white", self.Difficulty, self.TileSearchRange, self.Use_XTA,
                                    self.XTA_Coefficient, self.RunRemote)
                if self.RunRemote:
                    self.AI.startalphabeta()
            elif inputcmd == "cpuplay":
                if self.Turn == "cpu":
                    if not self.RunRemote:
                        self.AI.startalphabeta()
                    self.AI.choosemove()
                    while True:
                        result = self.AI.getresult()
                        if result:
                            movedata, hashdata = result[0], result[1]
                            break
                    self.GameBoard.addstone(movedata[1], "white")
                    print(movedata[1][0], movedata[1][1])
                    self.Turn = "player"
                else:
                    print("Invalid turn")
            elif inputcmd == "stoneinfo":
                if self.GameBoard:
                    print(" ".join([str(x for x in self.GameBoard.BlackStones)]))
                    print(" ".join([str(x for x in self.GameBoard.WhiteStones)]))
                else:
                    print("No game started")
            elif "placestone" in inputcmd:
                if len(inputcmd.split()) != 3:
                    print("Missing parameters")
                elif self.Turn == "cpu":
                    print("Invalid Turn")
                else:
                    x, y = inputcmd.split()[1], inputcmd.split()[2]
                    if x.isdigit() and y.isdigit():
                        if int(x) <= self.BoardSize_X and int(y) <= self.BoardSize_Y and int(x) > 0 and int(y) > 0:
                            self.GameBoard.addstone((int(x), int(y)), "black")
                            self.Turn = "cpu"
                        else:
                            print("Position out of bounds")
                    else:
                        print("Invalid parameters")
            elif "boardsize" in inputcmd:
                if len(inputcmd.split()) != 3:
                    print("Missing parameters")
                else:
                    x, y = inputcmd.split()[1], inputcmd.split()[2]
                    if x.isdigit() and y.isdigit():
                        self.BoardSize_X = int(x)
                        self.BoardSize_Y = int(y)
                    else:
                        print("Invalid parameters")
            else:
                print('Unknown command. Type "help" for help')


if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("Gomokubot(GomokuReloaded)")
    if not os.path.exists("settings.config"):
        print("Could not find settings.config file. Please verify that you have it in this directory.")
        sys.exit()
    parser = argparse.ArgumentParser(description="GomokuReloaded - a bot to play Gomoku half decently")
    parser.add_argument("-stdcomm", action="store_true", default=True, dest="stdcomm",
                        help="Use std i/o for playing")
    parser.add_argument("-nogui", action="store_true", default=True, dest="nogui",
                        help="Do not ever spawn the GUI (default)")
    parser.add_argument("-noconsole", action="store_true", default=False, dest="noconsole",
                        help="Do not even show the console (Use with caution)")
    parser.add_argument("-socket", nargs=2, type=str, dest="socket",
                        help="Use a socket connection instead of std i/o.", metavar=("address", "port"))
    parser.add_argument("-mcts", action="store_true", default=False, dest="mcts",
                        help="Use MCTS algorithm instead of Alpha-Beta")
    parser.add_argument("-debug", action="store_true", default=False, dest="debug",
                        help="Display debug info in stdout")
    if len(sys.argv) == 1:
        print("No additional arguments specified")
        usrinput = input("Would you like to run the User Interface Instead?(Y/N)")
        if usrinput in ["Y", "y"]:
            externmodulecall(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.config").replace("\\", "/"))
        else:
            print("Running in console mode. Waiting for input...")

    InputHandler(parser.parse_args(sys.argv[1:]),
                 os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.config").replace("\\", "/"))
