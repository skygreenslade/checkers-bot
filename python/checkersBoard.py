


# 0 = blank
# 2 = robot
# 3 = opponent
# 22 = robot king piece
# 33 = opponent king piece


# top of board is away from robot
boardState = [[0, 3, 0, 3, 0, 3, 0, 3],
              [3, 0, 3, 0, 3, 0, 3, 0],
              [0, 3, 0, 3, 0, 3, 0, 3],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [2, 0, 2, 0, 2, 0, 2, 0],
              [0, 2, 0, 2, 0, 2, 0, 2],
              [2, 0, 2, 0, 2, 0, 2, 0]]


newBoard =   [[0, 3, 0, 3, 0, 3, 0, 3],
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

    error = 0           #error code for function
    capture = False     #flag of if a piece was captured
    kingPiece = False   #boolean of if piece is a king piece or not
    piece = 0           #holds piece

    #convert given positions into array indices
    oldRow = getRow(oldPos[0])
    newRow = getRow(newPos[0])
    oldCol = getCol(oldPos[1])
    newCol = getCol(newPos[1])

    #check that given values were valid
    if oldRow == None or oldCol == None or oldCol == None or newCol == None:
        error  = 1 #invalid input

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

        #make king piece if piece made it top opposite end
        if piece == 2 and newRow == 0:
            boardState[newRow][newCol]*=11
        elif piece == 3 and newRow == 7:
            boardState[newRow][newCol]*=11


    return error
#move




#################### main ######################


exit = False



print("Welcome to the Checkers Board Script.")

newBoard = input("Press '0' for new board\n")


if newBoard == '0':
    boardState = newBoard
    
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

        if error == 1:
            print("Error: invalid input.")
        elif error == 2:
            print("Error: invalid move. Piece already at target destination")
        elif error == 3:
            print("Error: invalid move. Pieces must move one space diagonally, or two when capturing")
        elif error == 4:
            print("Error: invalid move. No opponent piece to capture")
        
        #output board state
        printBoard(boardState)



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






