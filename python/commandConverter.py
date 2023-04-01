

import math
import testSerial

#FIFO path
fifoPath = "../moves"

#distances in mm
LENGTH = 40 #side length of square 
A1CENTER = (86+12 + LENGTH/2, 0 + LENGTH/2) #center of A1 square on x-axis

#lengths of arms in mm
ARM_1 = 348
ARM_2 = 245





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

    if letter == '1':
        col = 0
    elif letter == '2':
        col = 1
    elif letter == '3':
        col = 2
    elif letter == '4':
        col = 3
    elif letter == '5':
        col = 4
    elif letter == '6':
        col = 5
    elif letter == '7':
        col = 6
    elif letter == '8':
        col = 7

    return col
#getCol



#returns theta 1 and theta 2 for given tuple x,y coords
#uses constants defined at top of script
def invKin(coordinates):
    x = coordinates[0]
    y = coordinates[1]
    
    #top and bottom term for theta 2 calculation
    topTerm = (x**2) + (y**2) - (ARM_1**2) - (ARM_2**2)
    bottomTerm = 2*ARM_1*ARM_2

    #calculate theta 2
    t2 = -math.acos(topTerm/bottomTerm)

    #top and bottom term for theta 1 calculation
    # topTerm = ARM_2*math.sin(t2)
    # bottomTerm = (ARM_1+(ARM_2*math.cos(t2)))
    
    #calculat theta 1
    # t1 = math.atan(y/x) + math.atan(topTerm/bottomTerm)

    topTerm = (x**2) + (y**2) + (ARM_1**2) - (ARM_2**2)
    bottomTerm = (2 * math.sqrt((x**2)+(y**2)) * ARM_1)

    t1 = math.atan(y/x) + math.atan(topTerm/bottomTerm) 


    return(t1, t2)
#invKin



#changes radians angles to those expected by the arduino
def convertRad(thetas):

    t1 = math.pi - thetas[0]
    t2 = -thetas[1]

    t1 = 180*t1/math.pi
    t2 = 180*t2/math.pi

    return (t1, t2)

#convertRad




def wait_for_arduino():
    while testSerial.arduino_ready is not True:
            pass
    
    print("Arduino Ready!")
    
#wait_for_arduino




#executes the commands for a move from thetas1 to thetas2
def movePiece(thetas1, thetas2):

    #move over position 1
    testSerial.move_robot(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()

    #pick up piece
    testSerial.pickup(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()

    #move ove position 2
    testSerial.move_robot(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()

    #place piece
    testSerial.drop(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()

#movePiece





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

        #calculate x,y cordinates of each position
        pos1 = (oldCol*LENGTH + A1CENTER[1], oldRow*LENGTH + A1CENTER[0])
        pos2 = (newCol*LENGTH + A1CENTER[1], newRow*LENGTH + A1CENTER[0])

        #calculate thetas for each position
        thetas1 = invKin(pos1)
        thetas2 = invKin(pos2)

        print(pos1)

        # print(thetas1[0]*180/math.pi, thetas1[1]*180/math.pi, thetas2[0]*180/math.pi, thetas2[1]*180/math.pi)
        print(thetas1[0]/math.pi, thetas1[1]/math.pi, thetas2[0]/math.pi, thetas2[1]/math.pi)
        # print(thetas1, thetas2)

        #convert thetas to appropriate values
        thetas1 = convertRad(thetas1)   
        thetas2 = convertRad(thetas2)


        movePiece(thetas1, thetas2)


print("\nProgram completed normally. Exiting.\n")
#main





