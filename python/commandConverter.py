

import math


#FIFO path
fifoPath = "../moves"

#LENGTHances in mm
LENGTH = 40 #side length of square 
A1CENTER = (150 + LENGTH/2, -30 + LENGTH/2) #center of A1 square on x-axis

#lengths of arms in mm
ARM_1 = 355
ARM_2 = 254





########################### FUNCTIONS ############################


#returns int of row corresponding to the letter given
#returns None on invalid input
def getRow(letter):

    row = None

    if letter == 'H' or letter == 'h':
        row = 7
    elif letter == 'G' or letter == 'g':
        row = 6
    elif letter == 'F' or letter == 'f':
        row = 5
    elif letter == 'E' or letter == 'e':
        row = 4
    elif letter == 'D' or letter == 'd':
        row = 3
    elif letter == 'C' or letter == 'c':
        row = 2
    elif letter == 'B' or letter == 'b':
        row = 1
    elif letter == 'A' or letter == 'a':
        row = 0


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
    if (not isinstance(col, int)) or col > 8 or col < 0:
        col = None
    
    return col
#getCol



#returns theta 1 and theta 2 for given tuple x,y coords
#uses constants defined at top of script
def invKin(coordinates):
    x = coordinates[0]
    y = coordinates[1]
    
    #top and bottom term for theta 2 calculation
    topTerm = x**2 + y**2 - ARM_1**2 - ARM_2**2
    bottomTerm = 2*ARM_1*ARM_2

    t2 = math.acos(topTerm/bottomTerm)

    #top and bottom term for theta 1 calculation
    topTerm = ARM_2*math.sin(t2)
    bottomTerm = (ARM_1+(ARM_2*math.cos(t2)))
    
    t1 = math.atan(y/x)-math.atan(topTerm/bottomTerm)

    return(t1, t2)
#invKin










############################ main #############################


exit = False
#x,y position of start of move, and end of move
pos1 = (None, None)
pos2 = (None, None)

#open FIFO
print("Opening FIFO")

try:
    fifo = open(fifoPath, "r")
except OSError as err: 
    print("Could not open FIFO, %s", err)
else:
    print("FIFO opened for reading.")


#read in from FIFO until closed
while not exit:
    cmd = fifo.readline()

    #if FIFO is closed, exit
    if len(cmd) == 0:
        exit = True
        print("FIFO closed from writer side.")
    
    #parse command
    else:

        #parse input. NO ERROR HANDLING (only valid commands passed from checkersBoard.py)
        params = cmd.split(' ')
        oldPos = params[1]
        newPos = params[2]


        oldRow = getRow(oldPos[0])
        newRow = getRow(newPos[0])
        oldCol = getCol(oldPos[1])
        newCol = getCol(newPos[1])

        #calculate cordinates of each position
        pos1 = (oldCol*LENGTH + A1CENTER[1], oldRow*LENGTH + A1CENTER[0])
        pos2 = (newCol*LENGTH + A1CENTER[1], newRow*LENGTH + A1CENTER[0])

        thetas1 = invKin(pos1)
        thetas2 = invKin(pos2)


        print(thetas1[0]*180/math.pi, thetas1[1]*180/math.pi, thetas2[0]*180/math.pi, thetas2[1]*180/math.pi)


print("\nProgram completed normally. Exiting.\n")
#main





