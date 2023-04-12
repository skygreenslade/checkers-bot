

import tkinter as tk
import os



#file which holds board state
boardFile = "./boardState.ini" 

#fifo to write robot's (legal) moves to
fifoPath = "../moves"


#constants
SQUARE_SIZE = 100
CIRCLE_SIZE = SQUARE_SIZE*0.9
CIRCLE_OFFSET = (SQUARE_SIZE - CIRCLE_SIZE)/2

DARK_COLOUR = "sienna4"#"saddle brown"
LIGHT_COLOUR = "#e3b776"#"tan1"
ROBOT_COLOUR = "#24170c"
OPPONENT_COLOUR = "wheat2"
KING_COLOUR = '#ebc405'

ROBOT_PIECE = 2
ROBOT_KING = 22
OPPONENT_PIECE = 3
OPPONENT_KING = 33
NO_PIECE = 0



global pieceToMove
global validPiece
global finalPos
global boardState

validPiece = False
finalPos = [0, 0]


# top of board is away from robot
newBoard =   [[0, 3, 0, 3, 0, 3, 0, 3],
              [3, 0, 3, 0, 3, 0, 3, 0],
              [0, 3, 0, 3, 0, 3, 0, 3],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [2, 0, 2, 0, 2, 0, 2, 0],
              [0, 2, 0, 2, 0, 2, 0, 2],
              [2, 0, 2, 0, 2, 0, 2, 0]]



########################## functions #############################



#read board state from file and return it as board matrix
def readBoard(boardFile):

    newState = newBoard
    newRow = 0 #position for new board
    newCol = -1 #position for new board

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
def writeBoard(boardFile):

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
                row += convertPiece(boardState[i][j])
        
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




def placePieces(circles, canvas):

    #destroy old pieces
    for row in range(0, len(circles)):
        for col in range(0, len(circles[row])):
            if circles[row][col] != 0:
                canvas.delete(circles[row][col])
                circles[row][col] = 0

    #place new pieces
    for row in range (0, len(boardState)):
        for col in range(0, len(boardState[i])):
            #robot regualr piece
            if boardState[row][col] == ROBOT_PIECE:
                circles[row][col] = canvas.create_oval(SQUARE_SIZE*col + CIRCLE_OFFSET, SQUARE_SIZE*row + CIRCLE_OFFSET, 
                                                    SQUARE_SIZE*col + CIRCLE_SIZE, SQUARE_SIZE*row + CIRCLE_SIZE, 
                                                    fill=ROBOT_COLOUR)
            #robot king piece
            elif boardState[row][col] == ROBOT_KING:
                circles[row][col] = canvas.create_oval(SQUARE_SIZE*col + CIRCLE_OFFSET*(3), SQUARE_SIZE*row + CIRCLE_OFFSET*(3), 
                                                    SQUARE_SIZE*col + CIRCLE_SIZE*(8/9), SQUARE_SIZE*row + CIRCLE_SIZE*(8/9), 
                                                    fill=KING_COLOUR, width=CIRCLE_SIZE/4, outline=ROBOT_COLOUR)
            #opponent regualar piece
            elif boardState[row][col] == OPPONENT_PIECE:
                circles[row][col] = canvas.create_oval(SQUARE_SIZE*col + CIRCLE_OFFSET, SQUARE_SIZE*row + CIRCLE_OFFSET, 
                                                    SQUARE_SIZE*col + CIRCLE_SIZE, SQUARE_SIZE*row + CIRCLE_SIZE, 
                                                    fill=OPPONENT_COLOUR)
            #opponent king piece
            elif boardState[row][col] == OPPONENT_KING:
                circles[row][col] = canvas.create_oval(SQUARE_SIZE*col + CIRCLE_OFFSET*(3), SQUARE_SIZE*row + CIRCLE_OFFSET*(3), 
                                                    SQUARE_SIZE*col + CIRCLE_SIZE*(8/9), SQUARE_SIZE*row + CIRCLE_SIZE*(8/9), 
                                                    fill=KING_COLOUR, width=CIRCLE_SIZE/4, outline=OPPONENT_COLOUR)

#placePieces




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





#returns int of col corresponding to the letter given
#returns None on invalid input
def invGetCol(letter):

    col= None

    if letter == 7:
        col= 'H'
    elif letter == 6:
        col= 'G'
    elif letter == 5:
        col= 'F'
    elif letter == 4:
        col= 'E'
    elif letter == 3:
        col= 'D'
    elif letter == 2:
        col= 'C'
    elif letter == 1:
        col= 'B'
    elif letter == 0:
        col= 'A'


    return col
#getCol




#returns int of row corresponding to the number system
#returns None on invalid input
def invGetRow(letter):

    row = None

    if letter == 0:
        row = '8'
    if letter == 1:
        row = '7'
    if letter == 2:
        row = '6'
    if letter == 3:
        row = '5'
    if letter == 4:
        row = '4'
    if letter == 5:
        row = '3'
    if letter == 6:
        row = '2'
    if letter == 7:
        row = '1'
    
    return row

#getRow










#moves piece at oldPos to newPos on given board (if movement is valid)
def move(oldPos, newPos):

    error = 0           #error code for function
    capture = False     #flag of if a piece was captured
    kingPiece = False   #boolean of if piece is a king piece or not
    piece = 0           #holds piece

    #hold coordinates of old and new position for piece
    oldRow = oldPos[0]
    newRow = newPos[0]
    oldCol = oldPos[1]
    newCol = newPos[1]


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

        #convert given indices into move command format
        oldPos[1] = invGetCol(oldPos[1])
        newPos[1] = invGetCol(newPos[1])
        oldPos[0] = invGetRow(oldPos[0])
        newPos[0] = invGetRow(newPos[0])


        #write to FIFO if move was a legal robot move
        if piece%3 != 0:
            output = 'mv' + ' ' + oldPos[1] + oldPos[0] + ' ' + newPos[1] + newPos[0] + '\n'
            oputMove(output)
            

    return error
#move




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




#outputs given string to given fifo
def oputMove(toOput):
    print("writing to fifo: ",toOput)

    #write to fifo
    fifo.write(toOput)
    fifo.flush()

#oputMove



def startWindow():

    global start

    #start window to select new or previous game
    start = tk.Tk()
    start.title("Checkers Board")
    # start.geometry("600x300")

    #text label
    text = tk.Label(master=start, text="Checkers Bot Controller")
    text.grid(row=0, columnspan=3, pady=50)

    #buttons for new/load game, calibrate
    buttonNew = tk.Button(master=start, text="New Game", command=newGame, width=10)
    buttonNew.grid(row=1, column=0, padx=20, pady=20, ipady=20, ipadx=10)

    buttonLoad = tk.Button(master=start, text="Load Game", command=loadGame, width=10)
    buttonLoad.grid(row=1, column=1, padx=20, pady=20, ipady=20, ipadx=10)

    buttonCalib = tk.Button(master=start, text="Calibrate", command=calibrate, width=10)
    buttonCalib.grid(row=1, column=2, padx=20, pady=20, ipady=20, ipadx=10)

    #padding
    pad = tk.Frame(master=start)
    pad.grid(row=3, pady=20)


    #run window until selection is made
    start.mainloop()

#startWindow







#use new game board
def newGame():

    global start

    global boardState
    boardState = newBoard

    start.destroy()
#newGame




#load game state from ini
def loadGame():

    global start

    global boardState
    boardState = readBoard(boardFile)

    start.destroy()
#loadGame





#open calibration window to send calibration commands
def calibrate():

    #destroy start window, open calibration window
    start.destroy()

    global calib
    calib = tk.Tk()
    calib.title("Checkers Bot Calibration")

    label = tk.Label(master=calib, text="Select a calibration command")
    label.grid(row=0, columnspan=2, padx=10, pady=10)

    #add buttons for calibration commands
    buttonCorners = tk.Button(master=calib, text="4 Corners", command=lambda: oputMove("4c 00 00\n"), width=9)
    buttonA = tk.Button(master=calib, text="Column A", command=lambda: oputMove("pk A1 A8\n"), width=9)
    buttonH = tk.Button(master=calib, text="Column H", command=lambda: oputMove("pk H1 H8\n"), width=9)
    button1 = tk.Button(master=calib, text="Row 1", command=lambda: oputMove("pk A1 H1\n"), width=9)
    button8 = tk.Button(master=calib, text="Row 8", command=lambda: oputMove("pk A8 H8\n"), width=9)


    buttonCorners.grid(row=1, column=0, padx=20, pady=10)
    buttonA.grid(row=2, column=0, padx=20, pady=10)
    buttonH.grid(row=3, column=0, padx=20, pady=10)
    button1.grid(row=2, column=1, padx=20, pady=10)
    button8.grid(row=3, column=1, padx=20, pady=10)


    buttonExit = tk.Button(master=calib, text="Exit Calibration", command=exitCalib)
    buttonExit.grid(row=5, columnspan=2, padx=5, pady=15)

    #loop until exit
    calib.mainloop()


    
#calibrate



#exit calibration window
def exitCalib():

    global calib
    calib.destroy()

    #return to start window
    startWindow()

#exitCalib




def selectPiece(event):

    global pieceToMove
    global validPiece
    global finalPos

    #detemine array indices
    col = event.x//SQUARE_SIZE
    row = event.y//SQUARE_SIZE

    #determine what piece, if any is there
    if circles[row][col] != 0:
         pieceToMove = [row, col]
         validPiece = True
    else:
         validPiece = False

#selectPiece




def movePiece(event):

    global pieceToMove
    global validPiece
    global finalPos

    #move piece and record position
    if validPiece:
        canvas.moveto(circles[pieceToMove[0]][pieceToMove[1]], event.x-(CIRCLE_SIZE/2), event.y-(CIRCLE_SIZE/2))
        finalPos[0] = event.y//SQUARE_SIZE
        finalPos[1] = event.x//SQUARE_SIZE



#movePiece




def releasePiece(event):

    global pieceToMove
    global validPiece
    global finalPos


    if validPiece:
        #reset flag
        validPiece = False

        #check if move was valid
        if (0 <= int(finalPos[0]) < 8) and (0 <= int(finalPos[1]) < 8):
            error = move(pieceToMove, finalPos)

            if not error:
                writeBoard(boardFile)

        #update board state and file
        boardState = readBoard(boardFile)
        placePieces(circles, canvas)
        # printBoard(boardState)



#releasePiece





############################ main function ################################


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



boardState = None

#call start window
startWindow()




#if board state not defined (start window was closed), exit program
if boardState is not None:


    #open main window
    window = tk.Tk()
    window.title("Checkers Board")
    window.geometry(str(SQUARE_SIZE*8)+"x"+str(SQUARE_SIZE*8))

    #create canvas
    canvas = tk.Canvas(window, width=SQUARE_SIZE*8, height=SQUARE_SIZE*8)
    canvas.pack()

    #create grid
    grid = [[0 for i in range(0, 8)]for j in range(0, 8)]
    lightSquare = False
    for i in range (0, 8):
        lightSquare = not lightSquare
        for j in range(0, 8):
            if lightSquare:
                grid[i][j] = canvas.create_rectangle(SQUARE_SIZE*i, SQUARE_SIZE*j, SQUARE_SIZE*(i+1), SQUARE_SIZE*(j+1), fill=LIGHT_COLOUR, width=0)
                lightSquare = False
            else:
                grid[i][j] = canvas.create_rectangle(SQUARE_SIZE*i, SQUARE_SIZE*j, SQUARE_SIZE*(i+1), SQUARE_SIZE*(j+1), fill=DARK_COLOUR, width=0)
                lightSquare = True


    #set up pieces
    circles = [[0 for i in range(0, 8)]for j in range(0, 8)]
    writeBoard(boardFile)
    placePieces(circles, canvas)

    #bind mouse functions
    window.bind('<Button-1>', selectPiece)
    window.bind('<Motion>', movePiece)
    window.bind('<ButtonRelease-1>', releasePiece)

    #loop
    window.mainloop()




print("Program completed normally.")



