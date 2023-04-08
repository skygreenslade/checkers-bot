
import os, sys #FIFOs

# 0 = blank
# 2 = robot
# 3 = opponent
# 22 = robot king piece
# 33 = opponent king piece


#fifo to write robot's (legal) moves to
fifoPath = "../moves"
fifo = None     #holds fd for fifo

#file which holds board state
boardFile = "./boardState.ini" 


# top of board is away from robot
newBoard =   [[0, 3, 0, 3, 0, 3, 0, 3],
              [3, 0, 3, 0, 3, 0, 3, 0],
              [0, 3, 0, 3, 0, 3, 0, 3],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [2, 0, 2, 0, 2, 0, 2, 0],
              [0, 2, 0, 2, 0, 2, 0, 2],
              [2, 0, 2, 0, 2, 0, 2, 0]]




#################### functions ########################



#read board state from file and return it as board matrix
def readBoard(boardFile):

    newState = newBoard
    newRow = 0 #position for new board
    newCol = -1 #position ofr new board

    #read in board file
    file = open(boardFile, "r")
    state = file.read()
    nextChar = state[1]

    #parse for checkers positions
    for i in range(0,len(state)-1):
        char = state[i]
        nextChar = state[i+1]
        
        #next checkers position reached
        if char == '[':
            #move to next square
            newCol+=2
            if newCol == 9:
                newRow += 1
                newCol = 0
            elif newCol == 8:
                newRow += 1
                newCol = 1
            
            #update board state
            newState[newRow][newCol] = convertFromPiece(nextChar)
        
    return newState

#readBoard





#write board state to given file boardFile
def writeBoard(board, boardFile):

    row = ""    #holds row to be printed
    rowNum = ord('8')    #number to pre/append to each row
    letRow = "   A  B  C  D  E  F  G  H"    # header and footer rows

    #open file
    file = open(boardFile, "w")

    #print header row of numbers
    file.write(letRow)
    file.write("\n")

    #for each row
    for i in range(0,8):
        #add row letter to front of row
        row = chr(rowNum)+ ' '

        #for each position in row
        for j in range (0,8):

            #unused spaces are blank
            if ((j+i)%2) == 0:
                row += "   "

            #add appropriate character to each space
            else:
                row += convertPiece(board[i][j])
        
        #add row letter to end of row an print row
        row += ' ' + chr(rowNum)
        file.write(row)
        file.write("\n")
        #decremenmt row letter for next row
        rowNum -= 1
    
    #bottom row of numbers  
    file.write(letRow)
    file.write("\n")
    
#writeBoard







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




#converts piece into code
# r, R into 2, 22. o, O into 3, 33. blank into 0
def convertFromPiece(piece):

    toRet = 0

    if piece == 'r':
        toRet = 2
    if piece == 'R':
        toRet = 22
    if piece == 'o':
        toRet = 3
    if piece == 'O':
        toRet = 33
    
    return toRet

#convertFromPiece




#outputs current state of given board in terminal
def printBoard(board):

    row = ""    #holds row to be printed
    rowNum = ord('8')    #number to pre/append to each row
    letRow = "   A  B  C  D  E  F  G  H"    # header and footer rows

    #print header row of numbers
    print(letRow)

    #for each row
    for i in range(0,8):
        #add row letter to front of row
        row = chr(rowNum)+ ' '

        #for each position in row
        for j in range (0,8):

            #unused spaces are blank
            if ((j+i)%2) == 0:
                row += "   "

            #add appropriate character to each space
            else:
                row += convertPiece(board[i][j])
        
        #add row letter to end of row an print row
        row += ' ' + chr(rowNum)
        print(row)
        #decremenmt row letter for next row
        rowNum -= 1
    
    #bottom row of numbers  
    print(letRow)

#printBoard




#returns int of col corresponding to the letter given
#returns None on invalid input
def getCol(letter):

    col= None

    if letter == 'H' or letter == 'h':
        col= 7
    elif letter == 'G' or letter == 'g':
        col= 6
    elif letter == 'F' or letter == 'f':
        col= 5
    elif letter == 'E' or letter == 'e':
        col= 4
    elif letter == 'D' or letter == 'd':
        col= 3
    elif letter == 'C' or letter == 'c':
        col= 2
    elif letter == 'B' or letter == 'b':
        col= 1
    elif letter == 'A' or letter == 'a':
        col= 0


    return col
#getCol




#returns int of row corresponding to the number system
#returns None on invalid input
def getRow(letter):

    row = None

    if letter == '8':
        row = 0
    if letter == '7':
        row = 1
    if letter == '6':
        row = 2
    if letter == '5':
        row = 3
    if letter == '4':
        row = 4
    if letter == '3':
        row = 5
    if letter == '2':
        row = 6
    if letter == '1':
        row = 7
    
    return row

#getRow


#moves piece at oldPos to newPos on given board (if movement is valid)
def move(oldPos, newPos, board):

    error = 0           #error code for function
    capture = False     #flag of if a piece was captured
    kingPiece = False   #boolean of if piece is a king piece or not
    piece = 0           #holds piece

    #hold coordinates of old and new position for piece
    oldRow = None
    newRow = None
    oldCol = None
    newCol = None

    #ensure arguments are long enough
    if len(oldPos) > 1 and len(newPos) > 1: 
        #convert given positions into array indices
        oldRow = getRow(oldPos[1])
        newRow = getRow(newPos[1])
        oldCol = getCol(oldPos[0])
        newCol = getCol(newPos[0])

    #check that given values were valid
    if oldRow is None or oldCol is None or oldCol is None or newCol is None:
        error  = 1 #invalid input
    elif isinstance(oldCol, type(None)) or isinstance(newCol, type(None)) or isinstance(oldRow, type(None)) or isinstance(newRow, type(None)):
        error = 1 #invalid input

    #check that the move only involves legal squares
    elif ((oldRow+oldCol)%2) == 0 or ((newRow+newCol)%2) == 0:
        error = 1 #invalid input

    #check if there is already a piece at new location
    elif boardState[newRow][newCol] != 0:
        error = 2 #illegal move: piece already at new location

    #proceed if no error is found
    if not error:

        #get piece to move
        piece = boardState[oldRow][oldCol]

        #check if piece is a king piece
        if piece > 10:
            kingPiece = True
    
        #check if move is legal for king piece
    
        #if a king piece is not moving one square diagonally 
        if kingPiece and (abs(oldRow-newRow) != 1 or abs(oldCol-newCol) != 1):
            
            # if piece did not "jump" over a space diagonally 
            if abs(oldRow-newRow) != 2 or abs(oldCol - newCol) != 2:
                error = 3 #illegal move: not how pieces move

            #if piece did not jump over an opponent piece
            elif boardState[(oldRow+newRow)//2][(oldCol+newCol)//2]%(piece%10) == 0:
                error = 4 #illegal move: no piece to capture

                #if prev cases are false, piece moved diagonally, over an opponent piece
            else:
                capture = True
        
        elif not kingPiece:
            
            #robot piece case, when not moving one space diagonally
            if piece == 2 and ((oldRow - newRow) != 1 or abs(oldCol - newCol) != 1):
                
                #if piece did not jump diagonally in the correct direction
                if (oldRow - newRow) != 2 or abs (oldCol - newCol) != 2:
                    error = 3 #illegal move: not how pieces move


                #if piece did not jump over an opponent piece
                elif boardState[(oldRow+newRow)//2][(oldCol+newCol)//2]%(piece%10) == 0:
                    error = 4 #illegal move: no piece to capture 

                #if previous cases are false, piece moved diagonally in the right direction, over an opponent piece 
                else:
                    capture = True
            
            #opponent piece case, when not moving one space diagonally
            elif piece == 3 and ((oldRow - newRow) != -1 or abs(oldCol - newCol) != 1):

                #if piece did not jump diagonally in the correct direction
                if (oldRow - newRow) != -2 or abs (oldCol - newCol) != 2:
                    error = 3 #illegal move: not how pieces move


                #if piece did not jump over an opponent piece
                elif boardState[(oldRow+newRow)//2][(oldCol+newCol)//2]%(piece%10) == 0:
                    error = 4 #illegal move: no piece to capture 

                #if previous cases are false, piece moved diagonally in the right direction, over an opponent piece 
                else:
                    capture = True


    #if no error, execute move
    if not error:
        
        #move piece from old location to new location
        piece = boardState[oldRow][oldCol]
        boardState[oldRow][oldCol] = 0
        boardState[newRow][newCol] = piece
        
        #remove piece if one was captured
        if capture:
            boardState[(oldRow+newRow)//2][(oldCol+newCol)//2] = 0

        #make king piece if piece made it to opposite end
        if piece == 2 and newRow == 0:
            boardState[newRow][newCol]*=11
        elif piece == 3 and newRow == 7:
            boardState[newRow][newCol]*=11


        #write to FIFO if move was a legal robot move
        if piece%3 != 0:
            output = cmd + ' ' + oldPos + ' ' + newPos + '\n'
            oputMove(output)
            

    return error
#move



#outputs given string to given fifo
def oputMove(toOput):
    print("writing to fifo: ",toOput)

    #write to fifo
    fifo.write(toOput)
    fifo.flush()

#oputMove








#################### main ######################


exit = False



print("Welcome to the Checkers Board Script.")

new = input("Press '0' for new board\n")


if new == '0':
    boardState = newBoard
else:
    boardState = readBoard(boardFile)
    
printBoard(boardState)


#create and open FIFO
try:
    os.mkfifo(fifoPath)
except OSError as err:
    if err.errno != 17:
        print("Failed to create FIFO, %s" % err)
try:
    print("opening FIFO. Will wait for reader.")
    fifo = open(fifoPath, 'w', 1)
except OSError as err:
    print("Error opening file, %s", err)







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

        if error == 1:
            print("Error: invalid input.")
        elif error == 2:
            print("Error: invalid move. Piece already at target destination")
        elif error == 3:
            print("Error: invalid move. Pieces must move one space diagonally, or two when capturing")
            print("Only king pieces may capture backwards.")
        elif error == 4:
            print("Error: invalid move. No opponent piece to capture")


        #output board state
        printBoard(boardState)

        #update board file with new state
        writeBoard(newBoard, boardFile)



    #print board state command
    elif cmd == 'b':
        printBoard(boardState)


 
    #help command
    elif cmd == "h" or cmd == "help":
        print("commands:")
        print("\t x,\t\t Exit program")
        print("\t mv,\t\t Move piece from coord X# to X#, eg: mv C1 D2")
        print("\t b, \t\t Print current board state")
        print("\t h, help,\t display this message")


    #default
    else:
        print("Sorry, that command is unrecognized. Enter \"help\" for help.")





print("\nProgram completed normally. Exiting.\n")
#end of main






