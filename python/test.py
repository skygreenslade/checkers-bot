import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#import commandConverter
import numpy as np
import math

#distances in mm
LENGTH = 40 #side length of square 
A1CENTER = (150 + LENGTH/2, -30 + LENGTH/2) #center of A1 square on x-axis

#lengths of arms in mm
ARM_1 = 355
ARM_2 = 254

def plot_robot_arm(theta):
    # Define the lengths of the robot arm segments
    L1 = ARM_1
    L2 = ARM_2

    # Calculate the x and y coordinates of the end effector
    x = L1*np.cos(theta[0]) + L2*np.cos(theta[0]+theta[1])
    y = L1*np.sin(theta[0]) + L2*np.sin(theta[0]+theta[1])

    # Plot the robot arm
    plt.plot([0, L1*np.cos(theta[0])], [0, L1*np.sin(theta[0])], 'b-', linewidth=2)
    plt.plot([L1*np.cos(theta[0]), x], [L1*np.sin(theta[0]), y], 'r-', linewidth=2)
    plt.plot(x, y, 'ko', markersize=10)

    # Set the axis limits and labels
    plt.xlim(-500, 500)
    plt.ylim(-500, 500)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Robot Arm Position')


#returns theta 1 and theta 2 for given tuple x,y coords
#uses constants defined at top of script
def invKin(coordinates):
    x = coordinates[0]
    y = coordinates[1]
    
    #top and bottom term for theta 2 calculation
    topTerm = (x**2) + (y**2) - (ARM_1**2) - (ARM_2**2)
    bottomTerm = 2*ARM_1*ARM_2

    #calculate theta 2
    t2 = math.acos(topTerm/bottomTerm)

    #top and bottom term for theta 1 calculation
    topTerm = ARM_2*math.sin(t2)
    bottomTerm = (ARM_1+(ARM_2*math.cos(t2)))
    
    #calculat theta 1
    t1 = math.atan(y/x) - math.atan(topTerm/bottomTerm)

    #use positive version of negative theta 1
    # if t1< 0:
    #     t1 = 2*math.pi + t1

    return(t1, t2)
#invKin

x_range = range(100, 350, 20)
y_range = range(100, 300, 20)

x, y = np.meshgrid(x_range, y_range)
coords = np.column_stack((x.ravel(), y.ravel()))

coords = [tuple(coord) for coord in coords]

angles = []
i = 0

for coord in coords:
    angles.append(invKin(coord))


# Define the animation function to update the plot with new joint angles
def animate(i):
    plt.clf()
    theta = angles[i]
    plot_robot_arm(theta)
    return []

# Create the animation
ani = FuncAnimation(plt.gcf(), animate, frames=len(coords), interval=10, blit=True)

# Show the plot
plt.show()


print(angles)