import ACSAnt
import globalPheroMatrix
import loadPuzzles
import time
import random

# Helper function used to generate a data representation of the puzzle for use
def createSudokuRepresentation(puzzle):

    # First task: represent the board [row-column] = digit
    sudokuBoard = {}
    currentSudokuNum = 0
    for i in range(1, int(len(puzzle) / 9) + 1): #1-9
        for j in range(1, int(len(puzzle) / 9) + 1): #1-9
            if(puzzle[currentSudokuNum] == "0"):
                sudokuBoard[str(i) + str(j)] = "123456789"
            else:
                sudokuBoard[str(i) + str(j)] = puzzle[currentSudokuNum]
            currentSudokuNum += 1

    # Second task: represent the units, 1 unit = [[row], [column] [3x3 block]], 27 units (9 rows, 9 columns, 9 (3x3 blocks))
    
    # Get all rows
    allRows = []
    count = 1
    row = []
    for i in sudokuBoard:
        if(count != (int(len(puzzle) / 9) + 1)): # not equal to 10
            row.append(i)
            count += 1
        else:
            allRows.append(row)
            row = [i]
            count = 2
    allRows.append(row)


    # Get all columns
    allColumns = []
    label = '123456789'
    for i in range(1, int(len(puzzle) / 9) + 1):
        column = []
        for j in label:
            column.append(j + str(i))
        allColumns.append(column)


    # Get all 3x3 blocks
    allBlocks = []
    for i in range(1, int(len(puzzle) / 9) + 1, 3): # 1-9 -> 1, 4, 7
        block = []
        for j in range(1, int(len(puzzle) / 9) + 1, 3): # 1-9 -> 1, 4, 7
            block.append(str(i) + str(j))
            block.append(str(i) + str(j + 1))
            block.append(str(i) + str(j + 2))
            block.append(str(i + 1) + str(j))
            block.append(str(i + 1) + str(j + 1))
            block.append(str(i + 1) + str(j + 2))
            block.append(str(i + 2) + str(j))
            block.append(str(i + 2) + str(j + 1))
            block.append(str(i + 2) + str(j + 2))
            allBlocks.append(block)
            block = []

    allUnits = []
    for i in allRows:
        allUnits.append(i)
    
    for i in allColumns:
        allUnits.append(i)

    for i in allBlocks:
        allUnits.append(i)


    # Third task: Get a dictionary that maps cells to their units (row, column and block)
    unitList = {}
    for i in sudokuBoard:
        result = []
        for j in allUnits:
            for k in j:
                if(i == k):
                    result.append(j)
        unitList[i] = result


    # Fourth task: Get a dictionary that maps cells to their peers
    peerList = {}
    for i in sudokuBoard:
        currentSet = set()
        result = unitList[i]
        for j in result:
            for k in j:
                if(i == k):
                    currentSet.update(set(j))
        currentSet.remove(i)
        peerList[i] = currentSet
    

    return sudokuBoard, allUnits, unitList, peerList


# This function will be used to reduce the Sudoku board further based on known values
def constraintPropagation():
    for i in sudokuBoard:

        if(len(sudokuBoard[i]) != 1):
            # First step of constraint propagation algorithm
            myPossibleValues = {"1","2","3","4","5","6","7","8","9"}
            myPeers = peerList[i]
            for j in myPeers:
                if(len(sudokuBoard[j]) == 1): # Is a fixed peer
                    if sudokuBoard[j] in myPossibleValues:
                        myPossibleValues.remove(sudokuBoard[j])

            # Convert set to string and update sudoku value set for the given cell
            myString = ""
            for j in sorted(myPossibleValues):
                myString += str(j)
            sudokuBoard[i] = myString

            # Second step of constraint propagation algorithm - check possibility of values in value set
            myValueSet = sudokuBoard[i]

            # Check all values in the value set against all peers, if it doesnt appear in peers use it
            for j in myValueSet:
                canUpdate = True
                for k in myPeers:
                    for l in sudokuBoard[k]:
                        if(j == l):
                            canUpdate = False
                if(canUpdate):
                    sudokuBoard[i] = j
                    break


# Function used to check if the board is confirmed to be solved
def isBoardSolved(board):
    for i in board:
        if(len(board[i]) > 1):
            return False

    return True 


# Ant Colony Systems Algorithm with BVE - Implementation based on primary research paper (Lloyd & Amos)
def acs():

    # Apply constraint propagation
    initialValues = {None}
    newValues = {}

    # Repeatedly apply constraint propagation until no more changes can be done
    while(initialValues != newValues): 
        initialValues = sudokuBoard.copy()
        constraintPropagation()
        newValues = sudokuBoard.copy()
    
    globalMatrix = globalPheroMatrix.initializeGlobalMatrix(givenPuzzle)

    c = len(sudokuBoard) # d^2
    tBest = 0

    # While the puzzle is not solved
    while(not(isBoardSolved(sudokuBoard))):

        # Give each ant a local copy of the puzzle and assign them to a different cell
        numAnts = 10
        antArr = []

        for i in range(numAnts):
            # Generate random cell location
            randomCell = str(random.randint(1, 9)) + str(random.randint(1, 9))
            antArr.append(ACSAnt.ant(sudokuBoard.copy(), allUnits, unitList, peerList, globalMatrix, 0, 0.9, 0, randomCell))

        # For number of cells
        for i in range(len(sudokuBoard)):
            # For each ant
            for j in antArr:
                # If the current cell is not fixed
                if(not(j.isCurrentCellFixed())):
                    j.fixCellValue_PropagateAndUpdate()
                j.move()

        # Find best ant
        bestAntIndex = 0
        mostCellsSpecified = 0 # fBest

        for i in range(len(antArr)):
            totalCells = antArr[i].numCellsSpecified - antArr[i].failCells
            if(totalCells >= mostCellsSpecified):
                mostCellsSpecified = totalCells
                bestAntIndex = i
        
        bestAnt = antArr[bestAntIndex]

        # Do global pheromone update

        # Calculate amount of pheromone to add, c is the total number of cells on the board
        deltaT = (c / (c - mostCellsSpecified))

        if(deltaT >= tBest):
            tBest = deltaT

            # Replace current best solution with the solution found by the best iteration ant
            for i in sudokuBoard:
                sudokuBoard[i] = bestAnt.sudokuBoard[i]
            
            # Update all pheromone values corresponding to values in the current best solution
            p = 0.9
            for i in globalMatrix:
                newPheromones = []
                for j in globalMatrix[i]:
                    newPheromones.append(((1 - p) * j) + (p * tBest))
                globalMatrix[i] = newPheromones

        # Do best value evaporation
        pBVE = 0.005
        tBest = (tBest * (1 - pBVE))
                    

# Function used to return the board as a numerical string
def getPuzzleSolution(board):
    result = ""

    for i in board:
        result += board[i]

    return result


def checkAnswer(puzzle):
    if(len(puzzle) != 81):
        return False
    else:
        for i in puzzle:
            if(int(i) == 0):
                return False
        return True
        
                
# Puzzle test
puzzleTests = loadPuzzles.puzzles
runAverage = 0.0

for a in range(1,4):
    print("RUN ", a)
    startSequence = time.time()
    
    for i in puzzleTests[7:11]:

        givenPuzzle = i[0]

        sudokuBoard, allUnits, unitList, peerList = createSudokuRepresentation(givenPuzzle)
        acs()

        while(not(checkAnswer(getPuzzleSolution(sudokuBoard)))):
            sudokuBoard, allUnits, unitList, peerList = createSudokuRepresentation(givenPuzzle)
            acs()
    
    print("Running Time (Seconds): ", format((time.time() - startSequence), '.7f'))
    runAverage += float(format((time.time() - startSequence), '.7f'))

print("3-Run Average: ", runAverage / 3)