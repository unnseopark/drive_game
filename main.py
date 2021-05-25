from random import shuffle, randrange, randint, choice
from cmu_112_graphics import *

def appStarted(app):
    app.width, app.height = gameDimensions()
    app.obstacleTypes = ["car", "truck", "bus", "bicycle"]
    app.obstacleColors = ["red", "yellow", "blue", "purple", "pink"]
    app.rows, app.cols, app.cellSize, app.mapWidth, app.mapHeight = mapSize(app)
    app.mapMargin = 10
    app.dirs = [(-1, 0), (0, -1), (1, 0)]
    app.gameStart = False
    app.helpPage = False
    
def restartGame(app, level):
    app.map = [[0] * app.cols for i in range(app.rows)]
    app.dir = 1
    app.mapCarW = app.cellSize * 7 / 30
    app.mapCarH = app.cellSize / 3
    app.AImode = False
    app.level = level
    app.gameWin = False
    app.gameOver = False
    app.vehicles = []
    makeMap(app)
    driver(app)
    scale(app)
    app.scrollX, app.scrollY = app.X - app.carX, app.Y - app.carY
    app.paused = False
    app.speed = 0.5
    createObstacles(app)

def driver(app):
    app.mapX = app.mapWidth / 2
    app.mapY = app.mapHeight - app.mapCarH
    app.driver = Vehicle(app, app.mapX, app.mapY, app.visited)
    app.driver.driver(app)
    app.vehicles.append(app.driver)

def scale(app):
    app.scale = app.cols * 5/ 2
    app.carW, app.carH = app.mapCarW * app.scale, app.mapCarH * app.scale
    app.X, app.Y = app.width / 2, app.height - app.carH
    app.carX, app.carY = app.mapX * app.scale, app.mapY * app.scale

def mapSize(app):
    width = app.width / 5
    rows = 21
    cols = 21
    cellSize = width / cols
    height = cellSize * rows
    return rows, cols, cellSize, width, height

# width and height of window
def gameDimensions():
    width = 500
    height = 750
    return width, height

def move(app):
    dx, dy = app.dirs[app.dir]
    app.mapX += dx * app.speed
    app.mapY += dy * app.speed
    #app.carY -= app.scale
    #app.carX, app.carY = app.mapX * app.scale, app.mapY * app.scale
    app.scrollX -= dx * app.scale * app.speed
    app.scrollY -= dy * app.scale * app.speed
    carOutofBound(app)
    reachDestination(app)
def keyPressed(app, event):
    if event.key == 'Up':
        move(app)
    if event.key == 'Left':
        changeDir(app, -1)
        carOutofBound(app)
        reachDestination(app)
    if event.key == 'Right':
        changeDir(app, 1)
        carOutofBound(app)
        reachDestination(app)
    if event.key == 'a':
        AImode(app)
        app.AImode = not app.AImode
    if event.key == 'p':
        app.paused = not app.paused
    if event.key == 1:
        app.speed = 0.5
    if event.key == 2:
        app.speed = 1
    if event.key == 3:
        app.speed = 1.5
    if event.key == 4:
        app.speed = 2
    if event.key == 5:
        app.speed = 2.5     
    if event.key == 'w':
        app.gameWin = True

def mousePressed(app, event):
    if app.gameStart == False and app.helpPage == False:
        if event.x > app.width / 2:
            app.gameStart = True
            restartGame(app, 1)
        if event.x < app.width / 2:
            app.helpPage = True
    elif app.helpPage:
        app.helpPage = False
    elif app.gameOver:
        restartGame(app, 1)
    elif app.gameWin:
        app.level += 1
        restartGame(app, app.level)

def AImode(app):
    speed = 1
    if len(app.mainRoad) > len(app.shortcut):
        road = app.shortcut
    else:
        road = app.mainRoad
    dx, dy = app.dirs[app.dir]
    newX = app.mapX + dx * app.cellSize / 2
    newY = app.mapY + dy * app.cellSize / 2
    newRow, newCol = getCell(app, newX, newY)
    currentRow, currentCol = getCell(app, app.mapX, app.mapY)
    nextRow, nextCol = road[road.index((currentRow, currentCol)) + 1]
    if (newRow, newCol) not in road:
        dx = nextCol - currentCol
        dy = nextRow - currentRow        
        newDir = (dx, dy)
        i = app.dir - app.dirs.index(newDir)
        changeDir(app, -i)
    aX0, aX1 = app.mapX - app.mapCarW / 2 - app.cellSize / 4, app.mapX + app.mapCarW / 2+ app.cellSize / 4
    aY0, aY1 = app.mapY - app.mapCarH / 2 - app.cellSize / 4, app.mapY + app.mapCarH / 2+ app.cellSize / 4
    # prevent from colliding with other vehicle
    for vehicle in app.vehicles[1:]:
        bX0, bX1, bY0, bY1 = vehicle.getMapBounds(app)
        if (aY0 <= (bY0 or bY1) <= aY1) and (aX0 <= (bX0 or bX1) <= aX1):
            app.mapX -= dx * speed
            app.mapY -= dy * speed
        if (bY0 <= (aY0 or aY1) <= bY1) and (bX0 <= (aX0 or aX1) <= bX1):
            app.mapX -= dx * speed
            app.mapY -= dy * speed
    app.mapX += dx * speed
    app.mapY += dy * speed
    app.scrollX -= dx * app.scale * speed
    app.scrollY -= dy * app.scale * speed
    reachDestination(app)

def changeDir(app, dir):
    if app.dir + dir >= 0 and app.dir + dir < len(app.dirs):
        app.dir += dir
        app.mapCarW, app.mapCarH = app.mapCarH, app.mapCarW
        app.carW, app.carH = app.carH, app.carW

def carOutofBound(app):
    rowA, colA = getCell(app, app.mapX - app.mapCarW/2, app.mapY - app.mapCarH/2)
    rowB, colB = getCell(app, app.mapX + app.mapCarW/2, app.mapY + app.mapCarH/2)
    cells = [(rowA, colA), (rowA, colB), (rowB, colA), (rowB, colB)]
    for (row, col) in cells:
        if (row, col) not in app.visited:
            app.gameOver = True
            return

def reachDestination(app):
    rowA, colA = getCell(app, app.mapX - app.mapCarW/2, app.mapY - app.mapCarH/2)
    rowB, colB = getCell(app, app.mapX + app.mapCarW/2, app.mapY + app.mapCarH/2)
    cells = [(rowA, colA), (rowA, colB), (rowB, colA), (rowB, colB)]
    for (row, col) in cells:
        if (row, col) == app.mainRoad[-1]:
            app.gameWin = True

def makeMap(app):
    dirs = [(0, 1), (0, -1), (-1, 0)]
    app.visited = [(app.rows - 1, app.cols // 2)]
    app.mainRoad = copy.deepcopy(app.visited)
    app.mainRoad = makeRoad(app, (app.rows - 2, app.cols // 2), (1, app.cols // 2), app.mainRoad, dirs)
    app.visited += copy.deepcopy(app.mainRoad)
    startIndex = len(app.mainRoad) //10
    endIndex = len(app.mainRoad) *9 // 10
    start = app.mainRoad[startIndex]
    end = app.mainRoad[endIndex]
    app.shortcut = copy.deepcopy(app.mainRoad[:startIndex])
    app.shortcut = makeRoad(app, start, end, app.shortcut, dirs)
    app.shortcut.pop()
    app.shortcut += copy.deepcopy(app.mainRoad[endIndex+1:])
    app.visited += copy.deepcopy(app.shortcut)
    app.roadVisited = app.visited
    app.roadMap = copy.deepcopy(app.map)

def makeRoad(app, start, end, road, dirs):
    rows, cols = app.rows, app.cols
    row, col = start
    def makeRoadHelper(row, col):
        road.append((row, col))
        if (row, col) == end:
            return True
        else:
            shuffle(dirs)
            for (dRow, dCol) in dirs:
                newRow, newCol = row + dRow, col + dCol
                if newRow in range(rows) and newCol in range(cols):
                    if (newRow, newCol) not in road:
                        counter = 0
                        d = [(0, 1), (0, -1), (-1, 0), (1, 0)]
                        for (dRow, dCol) in d:
                            if (newRow + dRow, newCol + dCol) in (road or app.visited):
                                counter += 1
                        if counter < 2:
                            if makeRoadHelper(newRow, newCol):
                                return True
            road.remove((row, col))
            return False
    if makeRoadHelper(row, col):
        for (row, col) in road:
            app.map[row][col] = 1
        road.append((0, app.cols // 2))
        app.map[0][app.cols // 2] = 2
        return road

#code for getCell copied with modifications 
#from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
def getCell(app, x, y):
    row = int(y / app.cellSize)
    col = int(x / app.cellSize)
    return row, col

#code for getCellBounds copied with modifications 
#from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
def getCellBounds(app, row, col):
    x0 = col * app.cellSize
    x1 = (col+1) * app.cellSize
    y0 = row * app.cellSize
    y1 = (row+1) * app.cellSize
    return x0, x1, y0, y1

def getRoadBounds(app, row, col):
    x0, x1, y0, y1 = getCellBounds(app, row, col)
    x0 = x0 * app.scale + app.scrollX 
    x1 = x1 * app.scale + app.scrollX 
    y0 = y0 * app.scale + app.scrollY 
    y1 = y1 * app.scale + app.scrollY 
    return x0, x1, y0, y1

############################################################################
# VIEW
############################################################################
def drawMapCells(app, canvas, mode):
    if mode == 'map':
        draw = app.map
    elif mode == 'road':
        draw = app.roadMap
    for row in range(app.rows):
        for col in range(app.cols):
            color = 'green'
            if mode == 'map':
                x0, x1, y0, y1 = getCellBounds(app, row, col)
                x0 += app.mapMargin
                x1 += app.mapMargin
                y0 += app.mapMargin
                y1 += app.mapMargin
            elif mode == 'road':
                x0, x1, y0, y1 = getRoadBounds(app, row, col)
            if draw[row][col] == 1:
                color = 'grey'
            if draw[row][col] == 2:
                color = 'pink'
            if draw[row][col] == 3:
                drawCrossWalk(app, canvas)
            canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 0)

def drawMapLanes(app, canvas):
    for (row, col) in [app.mainRoad[0], app.mainRoad[-1]]:
        x0, x1, y0, y1 = getCellBounds(app, row, col)
        x = (x0 + x1) / 2
        canvas.create_line(x, y0, x, y1, fill = 'white', width = 1)
    for i in range(1, len(app.mainRoad)-1):
        row, col = app.mainRoad[i]
        pRow, pCol = app.mainRoad[i-1]
        nRow, nCol = app.mainRoad[i+1]
        x0, x1, y0, y1 = getCellBounds(app, row, col)
        cX, cY = (x0 + x1) / 2, (y0 + y1) / 2
        if col == pCol:
            xS = cX
            yS = y0
            if row < pRow:
                yS = y1
        elif row == pRow:
            xS = x0
            if col < pCol:
                xS = x1
            yS = cY
        if col == nCol:
            xE = cX
            yE = y0
            if row < nRow:
                yE = y1
        elif row == nRow:
            xE = x0
            if col < nCol:
                xE = x1
            yE = cY
        canvas.create_line(xS, yS, cX, cY, xE, yE, fill = 'white', width = 1)
       
def drawMapDriver(app, canvas):
    x0 = app.mapX - app.mapCarW / 2 + app.mapMargin
    x1 = app.mapX + app.mapCarW / 2 + app.mapMargin
    y0 = app.mapY - app.mapCarH / 2 + app.mapMargin
    y1 = app.mapY + app.mapCarH / 2 + app.mapMargin
    canvas.create_rectangle(x0, y0, x1, y1, fill = 'black', width = 0)

def drawDriver(app, canvas):
    x0 = app.width / 2 - app.carW / 2
    x1 = app.width / 2 + app.carW / 2
    y1 = app.height - app.carH / 2
    y0 = y1 - app.carH
    canvas.create_rectangle(x0, y0, x1, y1, fill = 'black', width = 0)

def drawMapVehicle(app, canvas, vehicle):
    x0, x1, y0, y1 = getVehicleBounds(app, vehicle)
    color = vehicle.getColor()
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 0)

def drawVehicle(app, canvas, vehicle):
    x0, x1, y0, y1 = getVehicleBounds(app, vehicle)
    x0 = (x0 - app.mapMargin) * app.scale + app.scrollX
    x1 = (x1 - app.mapMargin) * app.scale + app.scrollX
    y0 = (y0 - app.mapMargin) * app.scale + app.scrollY
    y1 = (y1 - app.mapMargin) * app.scale + app.scrollY
    color = vehicle.getColor()
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 0)
       
def drawGameOver(app, canvas):
    y0, y1 = app.height / 3, app.height * 2/3
    canvas.create_rectangle(0, y0, app.width, y1, fill = 'Black')
    canvas.create_text(app.width/2, app.height/2, text = 'GAME OVER', 
                            font = 'Verdana 60 bold', fill = 'white')
    canvas.create_text(app.width/2, app.height/2 + 80, text = 'CLICK TO RESTART', fill = 'white', font = 'Verdana 20 bold')

def drawGameWin(app, canvas):
    y0, y1 = app.height / 3, app.height * 2/3
    canvas.create_rectangle(0, y0, app.width, y1, fill = 'Pink', width = 0)
    canvas.create_text(app.width/2, app.height/2, text = 'WIN', 
                            font = 'Verdana 90 bold', fill = 'Black')
    canvas.create_text(app.width/2, app.height/2 + 80, text = 'CLICK TO RESTART', fill = 'Black', font = 'Verdana 20 bold')


def drawMap(app, canvas):
    drawMapCells(app, canvas, 'map')
    drawMapDriver(app, canvas)
    canvas.create_rectangle(app.mapMargin, app.mapMargin, app.mapWidth + app.mapMargin, 
                            app.mapHeight + app.mapMargin, outline = 'yellow', width = 2)

def drawWindow(app, canvas):
    drawMapCells(app, canvas, 'road')
    drawDriver(app, canvas)
    canvas.create_text(app.width - 50, 10, text='Level: '+str(app.level))
    if app.AImode:
        canvas.create_text(app.width - 150, 10, text = 'AI Mode')

def frontPage(app, canvas):
    canvas.create_rectangle(0, 0, app.width / 2, app.height, fill = 'black', width = 0)
    canvas.create_rectangle(app.width /2, 0, app.width, app.height, fill = 'grey', width = 0)
    canvas.create_text(app.width*3 /4, app.height / 2, text = 'START GAME', font = 'Helvetica 30 bold')
    canvas.create_text(app.width /4, app.height / 2, text = 'HELP', font = 'Helvetica 30 bold', fill = 'white')
    canvas.create_text(app.width / 2, 100, text = 'DRIVE!', font = 'Helvetica 40 bold', fill = 'pink')

def drawHelpPage(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black', width = 0)
    font = 'Helvetica 20 '
    color = 'white'
    canvas.create_text(app.width / 2, 50, text = 'LEFT arrow key: turn left', font = font, fill = color)
    canvas.create_text(app.width / 2, 100, text = 'RIGHT arrow key: turn right', font = font, fill = color)
    canvas.create_text(app.width / 2, 150, text = 'Number Keys (1~5): adjust speed', font = font, fill = color)
    canvas.create_text(app.width / 2, 200, text = 'Press \'A\' to start AI mode', font = font, fill = color)
    canvas.create_text(app.width / 2, 330, text = 'Your goal is to reach the destination without ', font = font, fill = 'pink')
    canvas.create_text(app.width / 2, 360, text = 'exiting the road or bumping into other vehicles!', font = font, fill = 'pink')
    canvas.create_text(app.width / 2, 390, text = 'Every time you reach the destination, the level ', font = font, fill = 'pink')
    canvas.create_text(app.width / 2, 420, text = 'increasesand so does the difficulty.', font = font, fill = 'pink')
    canvas.create_text(app.width / 2, 450, text = 'Good Luck!', font = font, fill = 'pink')
    canvas.create_text(app.width / 2, app.height - 50, text = 'CLICK ANYWHERE TO EXIT PAGE', font = font, fill = color)
    
def redrawAll(app,canvas):
    if app.gameStart == False:
        frontPage(app, canvas)
        if app.helpPage == True:
            drawHelpPage(app, canvas)
    else:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = 'green', width = 0)
        drawWindow(app, canvas)
        drawMap(app, canvas)
        for vehicle in app.vehicles[1:]:
            drawMapVehicle(app, canvas, vehicle)
            drawVehicle(app, canvas, vehicle)
        if app.gameOver:
            drawGameOver(app, canvas)
        if app.gameWin:
            drawGameWin(app, canvas)

###############################################################################

def timerFired(app):
    if app.gameStart:
        if not app.gameOver and not app.paused and not app.gameWin:
            doStep(app)

def doStep(app):
    if app.AImode:
        AImode(app)
    i = 1
    while i in range(1, len(app.vehicles)):
        vehicle = app.vehicles[i]
        vehicle.move(app)
        i += 1
    driverCollide(app)
    move(app)

def playGame():
    width, height = gameDimensions()
    runApp(width = width, height = height)

#############################################################################
# Obstacles
#############################################################################
class Vehicle(object):
    def __init__(self, app, mapX, mapY, road):
        self.mapX, self.mapY = mapX, mapY
        self.dir = (0, -1)
        self.type = choice(app.obstacleTypes)
        self.color = choice(app.obstacleColors)
        self.speed = 0.01
        self.mapH = app.mapCarH
        self.mapW = app.mapCarW
        self.road = road
        if self.type == "truck":
            self.mapH *= 3/2
        elif self.type == "bus":
            self.mapH *= 2
        elif self.type == "bicycle":
            self.mapH /= 2
            self.mapW /= 3
        
    def __repr__(self):
        return str(self.getAttributes())
    def getAttributes(self):
        return (self.type, self.color, self.speed, self. mapX, self.mapY)
    def driver(self, app):
        self.type = "car"
        self.color = "black"
        self.speed = 0
        self.mapW, self.mapH = app.mapCarW, app.mapCarH
    def getSize(self):
        return self.mapW, self.mapH
    def getPosition(self):
        return self.mapX, self.mapY
    def setPosition(self, newX, newY):
        self.mapX, self.mapY = newX, newY
    def getMapBounds(self, app):
        x0 = self.mapX - self.mapW / 2
        x1 = self.mapX + self.mapW / 2
        y0 = self.mapY - self.mapH / 2
        y1 = self.mapY + self.mapH / 2
        return x0, x1, y0, y1
    def getColor(self):
        return self.color
    def getSpeed(self):
        return self.speed
    def setSpeed(self, newSpeed):
        self.speed = newSpeed
    def getDirection(self):
        return self.dir
    def changeDir(self, newDir):
        if self.dir != newDir:
            self.dir = newDir
            self.mapH, self.mapW = self.mapW, self.mapH
    def move(self, app):
        self.driverCollide(app)
        i = 0
        while i in range(len(app.vehicles)):
            other = app.vehicles[i]
            if other != self:
                if not vehiclesCollide(app, self, other):
                    dx, dy = self.dir
                    self.mapX += dx * self.speed
                    self.mapY += dy * self.speed
                    # change direction to make sure vehicle stays on road
                    lane = randrange(1, 4)
                    newX = self.mapX + dx * app.cellSize * lane / 4
                    newY = self.mapY + dy * app.cellSize * lane / 4
                    newRow, newCol = getCell(app, newX, newY)
                    currentRow, currentCol = getCell(app, self.mapX, self.mapY)
                    if (currentRow, currentCol) not in self.road:
                        return
                    if self.road.index((currentRow, currentCol))+1 >= len(self.road):
                        return
                    nextRow, nextCol = self.road[self.road.index((currentRow, currentCol)) + 1]
                    if (newRow, newCol) not in self.road:
                        dx = nextCol - currentCol
                        dy = nextRow - currentRow        
                        newDir = dx, dy
                        self.changeDir(newDir)
                else:
                    app.vehicles.remove(self)
                    addNewVehicle(app, 1)
            i += 1
        self.adjustSpeed(app)
        self.back(app)
    def back(self, app):
        row, col = getCell(app, self.mapX, self.mapY)
        if (row, col) == (self.road[-1] or self.road[0]):
            newRoad = []
            for i in self.road:
                newRoad.append(i)
            self.road = newRoad
            self.changeDir((0, 1))
    def driverCollide(self, app):
        aX0, aX1, aY0, aY1 = self.getMapBounds(app)
        bX0, bX1 = app.mapX - app.mapCarW / 2 - 10, app.mapX + app.mapCarW / 2 + 10
        bY0, bY1 = app.mapY- app.mapCarH / 2 - 10, app.mapCarH / 2 + 10
        if (bY0 <= (aY0 or aY1) <= bY1) and (bX0 <= (aX0 or aX1) <= bX1):
            self.mapX -= dx * self.speed
            self.mapY -= dy * self.speed
    def adjustSpeed(self, app):
        aX0, aX1, aY0, aY1 = self.getMapBounds(app)
        (dx, dy) = self.dir
        aX0 += dx * (app.cellSize / 4)
        aX1 += dx * (app.cellSize / 4)
        aY0 += dy * (app.cellSize / 4)
        for other in app.vehicles:
            if other != self:
                bX0, bX1, bY0, bY1 = other.getMapBounds(app)
                if (bY0 <= (aY0 or aY1) <= bY1) and (bX0 <= (aX0 or aX1) <= bX1):
                    if self.dir != other.getDirection():
                        self.mapX -= dx * self.speed
                        self.mapY -= dy * self.speed
                    else:
                        self.speed = other.getSpeed()

def addNewVehicle(app, i):
    road = choice([app.mainRoad, app.shortcut])
    row, col = road[i]
    x0, x1, y0, y1 = getCellBounds(app, row, col)
    prevRow, prevCol = road[i-1]
    if prevCol < col:
        dir = (1, 0) #west
        x = x0
        y = choice([y0 + (y1-y0)/4, (y0+y1)/2, y1 - (y1-y0)/4])
    elif prevCol > col:
        dir = (-1, 0) #east
        x = x1
        y = choice([y0 + (y1-y0)/4, (y0+y1)/2, y1 - (y1-y0)/4])
    elif prevRow > row:
        dir = (0, -1) #north
        x = choice([x0 + (x1-x0)/4, (x0+x1)/2, x1 - (x1-x0)/4])
        y = y1
    else: 
        return
    vehicle = Vehicle(app, x, y, road)
    vehicle.changeDir(dir)
    safe = True
    for other in app.vehicles:
        if vehiclesCollide(app, vehicle, other):
            safe = False
    if safe:
        app.vehicles.append(vehicle)

def obstacleDestination(app, vehicle):
    x0, x1, y0, y1 = vehicle.getMapBounds(app)
    rowA, colA = getCell(app, x0, y0)
    rowB, colB = getCell(app, x1, y1)
    cells = [(rowA, colA), (rowA, colB), (rowB, colA), (rowB, colB)]
    for (row, col) in cells:
        if (row, col) == app.mainRoad[-1]:
            vehicle.setRoad(app, newRoad)
            return
    
def vehiclesCollide(app, vehicleA, vehicleB):
    aX0, aX1, aY0, aY1 = vehicleA.getMapBounds(app)
    bX0, bX1, bY0, bY1 = vehicleB.getMapBounds(app)
    if (aY0 <= (bY0 or bY1) <= aY1) and (aX0 <= (bX0 or bX1) <= aX1):
        return True
    if (bY0 <= (aY0 or aY1) <= bY1) and (bX0 <= (aX0 or aX1) <= bX1):
        return True

# checks if collides with other vehicle
def driverCollide(app):
    aX0, aX1 = app.mapX - app.mapCarW / 2, app.mapX + app.mapCarW / 2
    aY0, aY1 = app.mapY - app.mapCarH / 2, app.mapY + app.mapCarH / 2
    for vehicle in app.vehicles:
        if vehicle != app.driver:
            bX0, bX1, bY0, bY1 = vehicle.getMapBounds(app)
            if (aY0 <= (bY0 or bY1) <= aY1) and (aX0 <= (bX0 or bX1) <= aX1):
                app.gameOver = True
                return True
            if (bY0 <= (aY0 or aY1) <= bY1) and (bX0 <= (aX0 or aX1) <= bX1):
                app.gameOver = True
                return True    

def getVehicleBounds(app, vehicle):
    vehicleWidth, vehicleHeight = vehicle.getSize()
    mapPosX, mapPosY = vehicle.getPosition()
    x0 = mapPosX - vehicleWidth / 2 + app.mapMargin
    x1 = mapPosX + vehicleWidth / 2 + app.mapMargin
    y0 = mapPosY - vehicleHeight / 2 + app.mapMargin
    y1 = mapPosY + vehicleHeight / 2 + app.mapMargin
    return x0, x1, y0, y1

def createObstacles(app):
    roadLength = min(len(app.mainRoad), len(app.shortcut))
    for i in range(1, app.level * 4):
        addNewVehicle(app, (i * roadLength)//(app.level * 4)+1)

#################################################
# main
#################################################

def main():
    playGame()

if __name__ == '__main__':
    main()