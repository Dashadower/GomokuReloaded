import configparser

configformat = [
    # Section name, value type, key name
    # refer to https://docs.python.org/3/library/configparser.html#supported-ini-file-structure
    ("GomokuBoardUI", int, "GRIDSIZE"),  # GomokuBoardUI board grid pixel size
    ("GomokuBoardUI", int, "BUFFER"),  # GomokuBoardUI buffer between end of Canvas and actual drawings
    ("GomokuBoard", int, "BOARDSIZE_X"),  # Gomoku Board x size
    ("GomokuBoard", int, "BOARDSIZE_Y"),  # Gomoku Board y size
    ("AI", str, "AIMODE"),  # AI type(ALPHABETA, MCTS)
    ("ALPHABETA", int, "DIFFICULTY"),  # Alpha-Beta search ply depth
    ("ALPHABETA", int, "SEARCHRANGE"),  # Alpha_Beta search field range(GetOpenMovesPlus)
    ("ALPHABETA", int, "USE_EXTENSIVE_ANALYSIS"),  # Alpha_Beta use XTA(AnalyzerOptimized)
    ("ALPHABETA", float, "EA_COEFFICIENT"),  # Alpha_Beta XTA amplification Coefficient
    ("MCTS", int, "TIMELIMIT"),  # MCTS time for each move
]
class ConfigReader:
    def __init__(self, config_file_path):
        self.FilePath = config_file_path
        self.Values = {}
        if not self.FilePath:
            print("ConfigReader Error: No config file path specified")
            raise Exception("ConfigReader: No config file path specified")
        else:
            self.CPParser = configparser.RawConfigParser()
            if not self.CPParser.read(self.FilePath):
                print("ConfigReader Error: No config file path specified!")
                raise Exception("ConfigReader: Unable to read config file: %s"%(self.FilePath))
            else:
                self.Parse()

    def Parse(self):
        for entry in configformat:
            data = entry[1](self.CPParser.get(entry[0], entry[2]))
            self.Values[entry[2]] = data

    def retrieve(self, value):
        return self.Values[value]

