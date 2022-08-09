import random
import neopixel

class LedArray:
    rows = 8
    cols = 8
    maxGenerations = 1000

    def __init__(self, pin):
        self.colour = 0
        self.currentGeneration = 0
        self.pixels = neopixel.NeoPixel(pin, 64)
        self.pixels.brightness = 0.1
        self.panel = [ [1, 1, 0, 0, 0, 0, 0, 0],
          [1, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 1, 0, 0, 0, 0],
          [0, 0, 1, 1, 0, 0, 1, 0],
          [0, 0, 1, 1, 0, 0, 1, 0],
          [0, 1, 0, 0, 0, 1, 1, 0],
          [0, 0, 0, 0, 1, 1, 0, 0],
          [0, 0, 0, 1, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0]
          ]
        self.reSeedPanel()


    def reSeedPanel(self) -> None:
        self.currentGeneration = 0
        i = random.randint(10,26)
        for j in range(i):
            self.panel[random.randint(0,LedArray.rows-1)][random.randint(0,LedArray.cols-1)] = random.randint(0,1)


    def colourWheel(self, pos):
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


    def GameOfLife(self) -> None:
        # Array to find 8 bordering cells to a given cell
        neighbourCells = [(1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (1,1)]

        # Copy the existing panel
        original = self.panel

        # Process panel.
        isStatic = True
        liveCells = 0
        outputPixel = 0
        for row in range(LedArray.rows):
            for col in range(LedArray.cols):
                # For each cell count the number of live neighbourCells.
                liveNeighbours = 0
                for neighbour in neighbourCells:
                    r = (row + neighbour[0])
                    c = (col + neighbour[1])
                    # Check the validity of the neighbouring cell and if it was originally a live cell.
                    if (r < LedArray.rows and r >= 0) and (c < LedArray.cols and c >= 0) and (original[r][c] == 1):
                        liveNeighbours += 1
                # Rule 1 or Rule 3
                if original[row][col] == 1 and (liveNeighbours < 2 or liveNeighbours > 3):
                    self.panel[row][col] = 0
                # Rule 4
                if original[row][col] == 0 and liveNeighbours == 3:
                    self.panel[row][col] = 1

                liveCells += self.panel[row][col]
                if original[row][col] != self.panel[row][col]:
                    isStatic = False
                # Output neopixels
                if self.panel[row][col] == 1:
                    self.pixels[outputPixel] = self.colourWheel(self.colour)
                else:
                    self.pixels[outputPixel] = (0, 0, 0)
                outputPixel += 1
                self.colour = (self.colour + 1) % 255

        if isStatic == True or liveCells <= 4 or self.currentGeneration > LedArray.maxGenerations:
            # Re-seed the panel
            self.reSeedPanel()

