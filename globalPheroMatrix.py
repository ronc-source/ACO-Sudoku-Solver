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
        if(count != (int(len(puzzle) / 9) + 1)): #not equal to 10
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
    for i in range(1, int(len(puzzle) / 9) + 1, 3): #1-9 -> 1, 4, 7
        block = []
        for j in range(1, int(len(puzzle) / 9) + 1, 3): #1-9 -> 1, 4, 7
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
def constraintPropagation(sudokuBoard, peerList):
    for i in sudokuBoard:

        if(len(sudokuBoard[i]) != 1):
            # First step of constraint propagation algorithm
            myPossibleValues = {"1","2","3","4","5","6","7","8","9"}
            myPeers = peerList[i]
            for j in myPeers:
                if(len(sudokuBoard[j]) == 1): #Is a fixed peer
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


# Ant Colony Systems Algorithm with BVE - From Paper
def acs(sudokuBoard, peerList):

    # Apply constraint propagation
    initialValues = {None}
    newValues = {}

    # Repeatedly apply constraint propagation until no more changes can be done
    while(initialValues != newValues):
        initialValues = sudokuBoard.copy()
        constraintPropagation(sudokuBoard.copy(), peerList.copy())
        newValues = sudokuBoard.copy()    


# Initialize global pheremone matrix (Possible value k = 1..9, cell index 1 - 81 (9^2), for dimension 9)
# Each element will have a fixed value 1/c, where c = 9^2
global globalPheroMatrix


def initializeGlobalMatrix(givenPuzzle):
    sudokuBoard, _, _, peerList = createSudokuRepresentation(givenPuzzle)
    acs(sudokuBoard, peerList)

    globalPheroMatrix = {}
    c = len(sudokuBoard) # d^2

    for i in sudokuBoard:
        # Cell is not fixed value
        if(len(sudokuBoard[i]) > 1):
            cell = [1/c] * len(sudokuBoard[i])
            globalPheroMatrix[i] = cell
        else:
            cell = [1/c]
            globalPheroMatrix[i] = cell
    
    return globalPheroMatrix