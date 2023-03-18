


# 0 = blank
# 1 = robot
# 2 = opponent
# 11 = robot king piece
# 22 = opponent king piece


# top of board is away from robot
boardState = [[0, 3, 0, 3, 0, 3, 0, 3],
              [3, 0, 3, 0, 3, 0, 3, 0],
              [0, 3, 0, 3, 0, 3, 0, 3],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [2, 0, 2, 0, 2, 0, 2, 0],
              [0, 2, 0, 2, 0, 2, 0, 2],
              [2, 0, 2, 0, 2, 0, 2, 0]]


#################### functions ########################


#converts given character into approporiate piece
#r = robot, o = oppoent, capital = king piece
#
def convertPiece(piece):

    toRet = "[ ]"

    #convert to appropriate output
    if piece == 2:
        toRet = "[r]"
    elif piece == 3:
        toRet = "[o]"
    elif piece == 22:
        toRet = "[R]"
    elif piece == 33:
        toRet = "[O]"

    return toRet

#convertPiece




#outputs current state of given board in terminal
def printBoard(board):

    row = ""    #holds row to be printed
    rowLetter = ord('H')    #letter to pre/append to each row
    numRow = "   1  2  3  4  5  6  7  8"    # header and footer rows

    #print header row of numbers
    print(numRow)

    #for each row
    for i in range(0,8):
        #add row letter to front of row
        row = chr(rowLetter)+ ' '

        #for each position in row
        for j in range (0,8):

            #unused spaces are blank
            if ((j+i)%2) == 0:
                row += "   "

            #add appropriate character to each space
            else:
                row += convertPiece(board[i][j])
        
        #add row letter to end of row an print row
        row += ' ' + chr(rowLetter)
        print(row)
        #decremenmt row letter for next row
        rowLetter -= 1
    
    #bottom row of numbers  
    print(numRow)

#printBoard


#returns int of row corresponding to the letter given
#returns None on invalid input
def getRow(letter):

    row = None

    if letter == 'H' or letter == 'h':
        row = 0
    elif letter == 'G' or letter == 'g':
        row = 1
    elif letter == 'F' or letter == 'f':
        row = 2
    elif letter == 'E' or letter == 'e':
        row = 3
    elif letter == 'D' or letter == 'd':
        row = 4
    elif letter == 'C' or letter == 'c':
        row = 5
    elif letter == 'B' or letter == 'b':
        row = 6
    elif letter == 'A' or letter == 'a':
        row = 7


    return row
#getRow


#returns int of column corresponding to the number system
#returns None on invalid input
def getCol(letter):

    col = None

    #convert to int, subtract one for 0 based indexing
    try:
        col = int(letter) - 1
    except:
        pass

    # set to Null if out of bounds
    if col > 8 or col < 0:
        col = None

    return col
#getCol


#moves piece at oldPos to newPos on given board (if movement is valid)
def move(oldPos, newPos, board):

    error = 0 #error code for function
    capture = False #flag of if a piece was captured

    #convert given positions into array indices
    oldRow = getRow(oldPos[0])
    newRow = getRow(newPos[0])
    oldCol = getCol(oldPos[1])
    newCol = getCol(newPos[1])

    #check that given values were valid
    if oldRow == None or oldCol == None or oldCol == None or newCol == None:
        error  = 1 #invalid input

    #check if there is already a piece at new location
    elif boardState[newRow][newCol] != 0:
        error = 2 #illegal nove: piece already at new location

    #check that the move only involves legal squares
    elif ((oldRow+oldCol)%2) == 0 or ((newRow+newCol)%2) == 0:
        error = 1 #invalid input
    
    #check that move either moves one square diagonally, or is jumping over an opponent piece
    elif abs(oldRow-newRow) != 1 or abs(oldCol-newCol) != 1:
        if abs(oldRow-newRow) != 2 or abs(oldCol - newCol) != 2:
            error = 3 #illegal move: not how pieces move
        elif boardState[(oldRow+newRow)//2][(oldCol+newCol)//2]%(boardState[oldRow][oldCol]%10) == 0:
            error = 4 #illegal move: no piece to capture 
        else:
            capture = True

    #if no error, execute move
    if error == 0:
        
        piece = boardState[oldRow][oldCol]
        boardState[oldRow][oldCol] = 0
        boardState[newRow][newCol] = piece
        
        #remove piece if one was captured
        if capture:
            boardState[(oldRow+newRow)//2][(oldCol+newCol)//2] = 0

    return error
#move




#################### main ######################


exit = False



print("Welcome to the Checkers Board Script.")

newBoard = input("Press '0' for new board\n")


if newBoard == '0':
    printBoard(boardState)




#run until user exits
while exit == False:

    # get user input
    inp = input("Enter a command. 'x' to exit.\n")

    # get command from input
    params = inp.split(' ')
    cmd = params[0]

    # act on given input
    #exit case
    if cmd == 'x':
        exit = True
    
    #move piece command
    elif cmd == 'mv':
        toMove = params[1]
        moveTo = params[2] 
        
        error = move(toMove, moveTo, boardState)
        print(error)

        # piece = boardState[oldrow][oldcol]
        # boardState[oldrow][oldcol] = 0
        # boardState[newrow][newcol] = piece
        
        printBoard(boardState)



 
    #help command
    elif cmd == "h" or cmd == "help":
        print("commands:")
        print("\t x,\t\t Exit program")
        print("\t mv,\t\t Move piece from coord X# to X#, eg: mv C1 D2")
        print("\t h, help,\t display this message")
    
    #default
    else:
        print("Sorry, that command is unrecognized. Enter \"help\" for help.")





print("\nProgram completed normally. Exiting.\n")
#end of main






