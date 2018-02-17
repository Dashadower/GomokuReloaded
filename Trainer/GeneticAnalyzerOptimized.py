from Agent.FilterStrings import Open2, Open3, Open4, Open5, Closed4, Open5Val


class Analyzer:
    def __init__(self, board, open2val, open3val, open4val, closed4val):
        self.Board = board
        self.Open2Val = open2val
        self.Open3Val = open3val
        self.Open4Val = open4val
        self.Closed4Val = closed4val

    def grader(self, stonetype):
        """
        Returns a score of self.Board from the stonetype perspective
        Current Execution time: O(n^2)
        I should try to minimize this"""
        score = 0
        passedstones = []
        mystones = self.Board.BlackStones if stonetype == "black" else self.Board.WhiteStones
        enemystones = self.Board.WhiteStones if stonetype == "black" else self.Board.BlackStones

        # Check Vertical repetitions
        for stone in sorted(mystones, key=lambda x: x[1]):
            x, y = stone
            if (x, y) not in passedstones:
                data = ""
                for g in range(0, 6):
                    if (x, y-1+g) in mystones and (x, y-1+g) not in passedstones:
                        data += "o"
                        passedstones.append((x, y-1+g))
                    elif (x, y-1+g) in enemystones:
                        data += "x"
                        if g != 0:
                            break    # This fixed the Problem!!!!! Push 9818399
                    elif y-1+g <= 0 or y-1+g > self.Board.Size[1]:
                        data += "w"
                    elif (x, y-1+g) not in mystones and (x, y-1+g) not in enemystones:
                        data += "-"

                if data == "xooooo" or data == "-ooooo" or data == "wooooo":
                    if (x, y+5) in mystones:

                        checker_increment = 0
                        while True:
                            if (x, y+checker_increment+1) in mystones:
                                checker_increment += 1
                            else:
                                break
                        for value in range(0, checker_increment):
                            passedstones.append((x, y+value))

                    else:
                            score += Open5Val
                else:
                    if data.count("o") >= 2:
                        score += self.parser(data)

        # Check Horizontal repetitions
        passedstones = []
        for stone in sorted(mystones, key=lambda x: x[0]):
            x, y = stone
            if (x, y) not in passedstones:
                data = ""
                for g in range(0, 6):
                    if (x-1+g, y) in mystones and (x-1+g, y) not in passedstones:
                        data += "o"
                        passedstones.append((x-1+g, y))
                    elif (x-1+g, y) in enemystones:
                        data += "x"
                        if g != 0:
                            break    # This fixed the Problem!!!!! Push 9818399
                    elif x-1+g <= 0 or x-1+g > self.Board.Size[0]:
                        data += "w"
                    elif (x-1+g, y) not in mystones and (x-1+g, y) not in enemystones:
                        data += "-"

                if data == "xooooo" or data == "-ooooo" or data == "wooooo":
                    if (x+5, y) in mystones:

                        checker_increment = 0
                        while True:
                            if (x+checker_increment+1, y) in mystones:
                                checker_increment += 1
                            else:
                                break
                        for value in range(0, checker_increment):
                            passedstones.append((x+value, y))

                    else:
                        score += Open5Val
                else:
                    if data.count("o") >= 2:
                        score += self.parser(data)

        passedstones = []

        for stone in sorted(mystones, key=lambda x: x[0]+x[1]):  # stone coord: (x-y,y+1)
            x, y = stone
            if (x, y) not in passedstones:
                data = ""
                for g in range(0, 6):
                    if (x-1+g, y-1+g) in mystones and (x-1+g, y-1+g) not in passedstones:
                        data += "o"
                        passedstones.append((x-1+g, y-1+g))
                    elif (x-1+g, y-1+g) in enemystones:
                        data += "x"
                        if g != 0:
                            break
                    elif x-1+g <= 0 or x-1+g > self.Board.Size[0] or y-1+g <= 0 or y-1+g > self.Board.Size[1]:
                        data += "w"
                    elif (x-1+g, y-1+g) not in mystones and (x-1+g, y-1+g) not in enemystones:
                        data += "-"

                if data == "xooooo" or data == "-ooooo" or data == "wooooo":
                    if (x+5, y+5) in mystones:
                        checker_increment = 0

                        while True:
                            if (x+checker_increment+1, y+checker_increment+1) in mystones:
                                checker_increment += 1
                            else:
                                break
                        for value in range(0, checker_increment):
                            passedstones.append((x+value, y+value))

                    else:

                        score += Open5Val
                else:
                    if data.count("o") >= 2:
                        score += self.parser(data)
        passedstones = []

        # check 5o`clock diagonal from 1,13 to 13,1 repetitions
        for stone in sorted(mystones, key=lambda x: x[1]-x[0], reverse=True):
            # stone coord(x-self.Board.Size[1]+y,y),but each time in g traverse, sub from y and add to x
            x, y = stone
            if (x, y) not in passedstones:
                data = ""
                for g in range(0, 6):
                    if (x-1+g, y+1-g) in mystones and (x-1+g, y+1-g) not in passedstones:
                        data += "o"
                        passedstones.append((x-1+g, y+1-g))
                    elif (x-1+g, y+1-g) in enemystones:
                        data += "x"
                        if g != 0:
                            break
                    elif x-1+g <= 0 or x-1+g > self.Board.Size[0] or y+1-g <= 0 or y+1-g > self.Board.Size[1]:
                        data += "w"
                    elif (x-1+g, y+1-g) not in mystones and (x-1+g, y+1-g) not in enemystones:
                        data += "-"

                if data == "xooooo" or data == "-ooooo" or data == "wooooo":
                    if (x+5, y-5) in mystones:
                        checker_increment = 0

                        while True:
                            if (x+checker_increment+1, y-checker_increment-1) in mystones:
                                checker_increment += 1
                            else:
                                break
                        for value in range(0, checker_increment):
                            passedstones.append((x+checker_increment, y-checker_increment))

                    else:
                        score += Open5Val
                else:
                    if data.count("o") >= 2:
                        score += self.parser(data)

        return score

    def parser(self, pattern):
        """Returns correspoding value for pattern.
        Added for simplicity"""
        if pattern in Open2:

            return self.Open2Val
        elif pattern in Open3:

            return self.Open3Val
        elif pattern in Open4:

            return self.Open4Val
        elif pattern in Open5:

            return Open5Val
        elif pattern in Closed4:
            return self.Closed4Val
        else:
            return 0


class WinChecker(Analyzer):
    def __init__(self, board):
        super().__init__(board)

    def checkboth(self):
        patterns = super().grader("black")
        if patterns >= Open5Val:
            return True
        patterns = super().grader("white")
        if patterns >= Open5Val:
            return True
        else:
            return False

    def check(self, stonetype):
        """Check if a 5x exists for StoneType in self.GameBoard. Pretty much a copy of Analyzer() :p"""
        foundpatterns = super().grader(stonetype)
        if foundpatterns >= Open5Val:
            return True
        else:
            return False


