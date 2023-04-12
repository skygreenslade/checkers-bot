

import math
import testSerial
import time

#FIFO path
fifoPath = "../moves"

#distances in mm
LENGTHX = 40 #side length of square in x direction
LENGTHY = 40 #side length of square in y direction
A1CENTER = ( 0 + LENGTHX/2, 87+64 + LENGTHY/2) #center of A1 square on x-axis

#lengths of arms in mm
ARM_1 = 348 - 9 -5
ARM_2 = 225 - 5    #was 225





########################### FUNCTIONS ############################


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
        row = 7
    if letter == '7':
        row = 6
    if letter == '6':
        row = 5
    if letter == '5':
        row = 4
    if letter == '4':
        row = 3
    if letter == '3':
        row = 2
    if letter == '2':
        row = 1
    if letter == '1':
        row = 0
    
    return row

#getRow



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
    topTerm = ARM_2*math.sin(t2)
    bottomTerm = (ARM_1+(ARM_2*math.cos(t2)))
    
    #calculat theta 1
    t1 = math.atan(y/x) - math.atan(topTerm/bottomTerm)

    # topTerm = (x**2) + (y**2) + (ARM_1**2) - (ARM_2**2)
    # bottomTerm = (2 * math.sqrt((x**2)+(y**2)) * ARM_1)

    # t1 = math.atan(y/x) + math.atan(topTerm/bottomTerm) 


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
    arduino_ready = False
    while arduino_ready is not True:
        arduino_ready = testSerial.read_serial()

    print("Arduino Ready!")
    
#wait_for_arduino




#executes the commands for a move from thetas1 to thetas2
def movePiece(thetas1, thetas2):

    testSerial.move_robot(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.pickup(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.move_robot(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.drop(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()
    time.sleep(1)
#movePiece


def returnHome():
    testSerial.move_robot(40, 135)
    #wait_for_arduino()
    time.sleep(1)



def corners():

    #get corner coordinates
    corner1 = (0*LENGTHX + A1CENTER[0], 0*LENGTHY + A1CENTER[1])
    corner2 = (0*LENGTHX + A1CENTER[0], 7*LENGTHY + A1CENTER[1])
    corner3 = (7*LENGTHX + A1CENTER[0], 7*LENGTHY + A1CENTER[1])
    corner4 = (7*LENGTHX + A1CENTER[0], 0*LENGTHY + A1CENTER[1])

    #get corner thetas
    thetasC1 = invKin(corner1)
    thetasC2 = invKin(corner2)
    thetasC3 = invKin(corner3)
    thetasC4 = invKin(corner4)


    #send commands to poke each corner
    testSerial.move_robot(float(thetasC1[0]), float(thetasC1[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetasC1[0]), float(thetasC1[1]))
    wait_for_arduino()
    time.sleep(1)

    testSerial.move_robot(float(thetasC2[0]), float(thetasC2[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetasC2[0]), float(thetasC2[1]))
    wait_for_arduino()
    time.sleep(1)

    testSerial.move_robot(float(thetasC3[0]), float(thetasC3[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetasC3[0]), float(thetasC3[1]))
    wait_for_arduino()
    time.sleep(1)

    testSerial.move_robot(float(thetasC4[0]), float(thetasC4[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetasC4[0]), float(thetasC4[1]))
    wait_for_arduino()
    time.sleep(1)

#corners




#poke two squares given
def poke(pos1, pos2):


    #convert string to positions
    row1 = getRow(pos1[1])
    row2 = getRow(pos2[1])
    col1 = getCol(pos1[0])
    col2 = getCol(pos2[0])

    #calculate x,y cordinates of each position
    pos1 = (col1*LENGTHX + A1CENTER[0], row1*LENGTHY + A1CENTER[1])
    pos2 = (col2*LENGTHX + A1CENTER[0], row2*LENGTHY + A1CENTER[1])

    #calculate thetas
    thetas1 = invKin(pos1)
    thetas2 = invKin(pos2)

    #poke squares
    testSerial.move_robot(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetas1[0]), float(thetas1[1]))
    wait_for_arduino()
    time.sleep(1)

    testSerial.move_robot(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()
    time.sleep(1)
    testSerial.poke(float(thetas2[0]), float(thetas2[1]))
    wait_for_arduino()
    time.sleep(1)


#def poke




#converts command positions into movements and executes 
def moveCommand(oldPos, newPos):

    oldRow = getRow(oldPos[1])
    newRow = getRow(newPos[1])
    oldCol = getCol(oldPos[0])
    newCol = getCol(newPos[0])

    #calculate x,y cordinates of each position
    pos1 = (oldCol*LENGTHX + A1CENTER[0], oldRow*LENGTHY + A1CENTER[1])
    pos2 = (newCol*LENGTHX + A1CENTER[0], newRow*LENGTHY + A1CENTER[1])

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

#moveCommand




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

        #move command
        if params[0] == 'mv':
            moveCommand(params[1], params[2])
            
        # 4 corners command
        elif params[0] == '4c':
            corners()

        # poke (2 given squares) command
        elif params[0] == 'pk':
            poke(params[1], params[2])


        returnHome()            # move the robot arm to a position off of the board




print("\nProgram completed normally. Exiting.\n")
#main





