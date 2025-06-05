import random

class ant:
    def __init__(self, sudokuBoard, allUnits, unitList, peerList, globalPheroMatrix, failCells, greediness, 
                 numCellsSpecified, currentCell):
        self.sudokuBoard = sudokuBoard
        self.allUnits = allUnits
        self.unitList = unitList
        self.peerList = peerList
        self.globalPheroMatrix = globalPheroMatrix
        self.failCells = failCells 
        self.greediness = greediness
        self.numCellsSpecified = numCellsSpecified
        self.currentCell = currentCell
    

    # Move the ant to the next cell
    def move(self):
        if(int(self.currentCell[0]) == 9 and int(self.currentCell[1]) == 9):
            self.currentCell = "11"
        elif(int(self.currentCell[0]) != 9 and int(self.currentCell[1]) == 9):
            newRow = str(int(self.currentCell[0]) + 1)
            newCol = "1"
            self.currentCell = newRow + newCol
        else:
            newCol = str(int(self.currentCell[1]) + 1)
            self.currentCell = self.currentCell[0] + newCol


    # Check if its current cell is fixed
    def isCurrentCellFixed(self):
        if(len(self.sudokuBoard[self.currentCell]) > 1):
            return False
        else:
            return True
        

    # Choose and return a value from the current cell's value set - greediness param q0 = 1
    def chooseCurrentCellValue(self):
        randomIndex = random.randint(0, len(self.sudokuBoard[self.currentCell]) - 1)
        return self.sudokuBoard[self.currentCell][randomIndex], randomIndex
        

    # Propagate Constrains
    def constraintPropagation(self):

        for i in self.sudokuBoard:

            if(len(self.sudokuBoard[i]) != 1):

                # First step of constraint propagation algorithm
                myPossibleValues = {"1","2","3","4","5","6","7","8","9"}
                myPeers = self.peerList[i]
                for j in myPeers:
                    if(len(self.sudokuBoard[j]) == 1): #Is a fixed peer
                        if self.sudokuBoard[j] in myPossibleValues:
                            myPossibleValues.remove(self.sudokuBoard[j])

                # Convert set to string and update sudoku value set for the given cell
                myString = ""
                for j in sorted(myPossibleValues):
                    myString += str(j)
                self.sudokuBoard[i] = myString

                # Second step of constraint propagation algorithm - check possibility of values in value set
                myValueSet = self.sudokuBoard[i]

                # Check all values in the value set against all peers, if it doesnt appear in peers use it
                for j in myValueSet:
                    canUpdate = True
                    for k in myPeers:
                        for l in self.sudokuBoard[k]:
                            if(j == l):
                                canUpdate = False
                    if(canUpdate):
                        self.sudokuBoard[i] = j
                        break


    # Fix and propagate cells
    def fixCellValue_PropagateAndUpdate(self):

        # Get new cell value that will make it fixed
        newCellValue, globalPheroIndex = self.chooseCurrentCellValue()

        # Update the value set of the current cell
        self.sudokuBoard[self.currentCell] = newCellValue
        self.numCellsSpecified += 1

        # Apply constraint propagation
        initialValues = {None}
        newValues = {}

        # Repeatedly apply constraint propagation until no more changes can be done
        while(initialValues != newValues):
            initialValues = self.sudokuBoard.copy()
            self.constraintPropagation()
            newValues = self.sudokuBoard.copy()
        
        # Check fail cells (value set is size 0)
        for i in self.sudokuBoard:
            if(len(self.sudokuBoard[i]) < 1):
                self.failCells += 1

        # Update local pheromone

        # Every time an ant selects a value s at cell i, its pheromone value in the global pheromone matrix is updated

        xi = 0.1 # Standard setting for ACS

        # Update pheromone value in the global pheromone matrix
        originalPheroValue = self.globalPheroMatrix[self.currentCell][globalPheroIndex]
        self.globalPheroMatrix[self.currentCell][globalPheroIndex] = ((1 - xi) * originalPheroValue) + (xi * (1 / (len(self.sudokuBoard))))