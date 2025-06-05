import csv

puzzles = [] 

# Replace sudoku17.txt with any other sudoku CSV file
with open("sudoku17.txt", "rt") as myFile:
    capture = csv.reader(myFile)

    for i in capture:
        puzzles.append(i)
        if(len(puzzles) == 100):
            break