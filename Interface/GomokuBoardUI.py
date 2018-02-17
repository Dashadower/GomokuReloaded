# -*- coding:utf-8 -*-
import tkinter


class GomokuBoardUI(tkinter.Frame):
    def __init__(self, gameboard, master, gamemanager, gridsize=50, buffer=20):
        self.master = master
        tkinter.Frame.__init__(self, self.master)
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.GameBoard = gameboard

        self.gridsize = gridsize  # in settings.config
        self.stonesize = self.gridsize / 2
        self.buffer = buffer  # in settings.config
        self.GameArea = tkinter.Canvas(self, bg="green")
        self.GameArea.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.GameArea.bind("<Motion>", self.onmmousemove)
        self.GameArea.bind("<Button-1>", self.onmouseclick)
        self.GameManager = gamemanager
        self.PlayerTurn = False
        self.draw()

    def translatecoordinates(self, coord):
        """input : coord: tuple (x,y)
        output: translatedcoord : tuple (grid_x,grid_y)
        converts screen coordinates to gameboard coordinates(bottom left is 0,0)"""
        x, y = coord[0] - self.buffer, coord[1] - self.buffer
        x_grid_pos = divmod(x, self.gridsize / 2)[0] + 1
        x_grid_pos = int(divmod(x_grid_pos, 2)[0] + 1)

        y_grid_pos = divmod(y, self.gridsize / 2)[0] + 1
        y_grid_pos = int(self.GameBoard.Size[1] - (divmod(y_grid_pos, 2)[0]))
        return x_grid_pos, y_grid_pos

    def clear(self):
        self.GameArea.delete("all")

    def addstoneshape(self, color, position):
        position_x = position[0]-1
        position_y = self.GameBoard.Size[1]-position[1]
        self.GameArea.create_oval((self.buffer + position_x * self.gridsize - self.stonesize, self.buffer + position_y * self.gridsize + self.stonesize, self.buffer + position_x * self.gridsize + self.stonesize,
                                   self.buffer + position_y * self.gridsize - self.stonesize), fill=color, outline=color)

    def draw(self):
        for x in range(0, self.GameBoard.Size[0]-1):
            for y in range(0, self.GameBoard.Size[1]-1):  # create square grid

                self.GameArea.create_rectangle((self.buffer+self.gridsize*x, self.buffer+self.gridsize*y,
                                                self.buffer+self.gridsize*x+self.gridsize,
                                                self.buffer+self.gridsize*y+self.gridsize))

        for x in range(1, self.GameBoard.Size[0]+1):  # create x axis labels
            self.GameArea.create_text((self.buffer + self.gridsize * (x-1),
                                       self.buffer+self.gridsize*(self.GameBoard.Size[0]-1)+self.buffer/2), text=x)

        for y in range(1, self.GameBoard.Size[1]+1):  # create y axis labels
            self.GameArea.create_text((self.buffer/2, self.buffer+self.gridsize*(self.GameBoard.Size[1]-y)), text=y)

        for stone in self.GameBoard.BlackStones:  # draw existing black stones
            x = stone[0]-1
            y = self.GameBoard.Size[1]-stone[1]
            self.GameArea.create_oval((self.buffer+x*self.gridsize-self.stonesize,
                                       self.buffer+y*self.gridsize+self.stonesize,
                                       self.buffer+x*self.gridsize+self.stonesize,
                                       self.buffer+y*self.gridsize-self.stonesize), fill="black")

        for stone in self.GameBoard.WhiteStones:  # draw existing white stones
            x = stone[0]-1
            y = self.GameBoard.Size[1]-stone[1]
            self.GameArea.create_oval((self.buffer+x*self.gridsize-self.stonesize,
                                       self.buffer+y*self.gridsize+self.stonesize,
                                       self.buffer+x*self.gridsize+self.stonesize,
                                       self.buffer+y*self.gridsize-self.stonesize), fill="white", outline="white")

    def onmmousemove(self, event):
        x_grid_pos, y_grid_pos = self.translatecoordinates((event.x, event.y))
        if self.PlayerTurn:
            if x_grid_pos <= self.GameBoard.Size[0] and x_grid_pos >= 1:
                if y_grid_pos <= self.GameBoard.Size[1] and y_grid_pos >= 1:
                    if (x_grid_pos, y_grid_pos) not in self.GameBoard.BlackStones + self.GameBoard.WhiteStones:
                        self.clear()
                        self.draw()
                        self.addstoneshape(self.GameBoard.Turn, (x_grid_pos, y_grid_pos))
                    else:
                        self.clear()
                        self.draw()
                else:
                    self.clear()
                    self.draw()
            else:
                self.clear()
                self.draw()
        else:
            self.clear()
            self.draw()

    def onmouseclick(self, event):
        gridpos = self.translatecoordinates((event.x, event.y))
        if self.PlayerTurn:
            if gridpos not in self.GameBoard.BlackStones + self.GameBoard.WhiteStones and gridpos[0] <= self.GameBoard.Size[0] and gridpos[0] >= 1 and gridpos[1] <= self.GameBoard.Size[0] and gridpos[1] >= 1:

                if self.GameManager:
                    self.GameManager.registeruserstone(gridpos)
                else:
                    self.GameBoard.addstone(gridpos, self.GameBoard.Turn)
            self.clear()
            self.draw()
    def lockscreen(self):
        self.PlayerTurn = False


if __name__ == "__main__":
    from Agent.GameBoard import GameBoard
    board = GameBoard(15, 15)
    root = tkinter.Tk()
    boardui = GomokuBoardUI(board, root, None)
    boardui.PlayerTurn = True
    boardui.draw()

    root.mainloop()
