import serial
import struct
import time
import threading
import tkinter as tk

# Configure the serial port
ser = serial.Serial(
    port="/dev/ttyUSB0",  # Replace with your port (e.g., '/dev/ttyACM0' or '/dev/ttyUSB0' on Linux systems)
    baudrate=115200,
    timeout=1
)

# Packet markers
PACKET_START = 0x7E
PACKET_END = 0x7F

joint1_global = 0
joint2_global = 0

def send_packet(joint1, joint2, state):
    # Convert the float values to byte arrays
    joint1_bytes = struct.pack('<f', joint1)
    joint2_bytes = struct.pack('<f', joint2)

    bot_state = state
    # Build the packet
    packet = bytearray([PACKET_START]) + joint1_bytes + joint2_bytes + bytearray([bot_state]) + bytearray([PACKET_END])
    print("Sending packet:", [hex(b) for b in packet])

    # Send the packet
    ser.write(packet)

def move_robot(joint1, joint2):
    send_packet(joint1, joint2, 0)              # send a packet with nothing

def pickup(joint1, joint2):
    send_packet(joint1, joint2, 2)              # pickup state = 2

def drop(joint1, joint2):
    send_packet(joint1, joint2, 4)              # drop state = 4


def read_serial():
    while True:
        line = ser.readline()
        if line:
            try:
                print(line.decode('ascii').strip())
            except UnicodeDecodeError:
                print("Received binary data:", [hex(b) for b in line])

def on_send_button_click():
    try:
        joint1 = float(joint1_entry.get())
        joint2 = float(joint2_entry.get())
        move_robot(joint1, joint2)
    except ValueError:
        print("Invalid input. Please enter valid joint angles.")

def on_pickup_button_click():
    try:
        joint1 = float(joint1_entry.get())
        joint2 = float(joint2_entry.get())
        pickup(joint1, joint2 )
    except ValueError:
        print("Pickup error")

def on_drop_button_click():
    try:
        joint1 = float(joint1_entry.get())
        joint2 = float(joint2_entry.get())
        drop(joint1, joint2)
    except ValueError:
        print("drop error")

# Create a GUI for user input
root = tk.Tk()
root.title("Joint Angle Sender")

joint1_label = tk.Label(root, text="Joint 1 Angle (degrees):")
joint1_label.grid(row=0, column=0, padx=10, pady=10)
joint1_entry = tk.Entry(root)
joint1_entry.grid(row=0, column=1)

joint2_label = tk.Label(root, text="Joint 2 Angle (degrees):")
joint2_label.grid(row=1, column=0, padx=10, pady=10)
joint2_entry = tk.Entry(root)
joint2_entry.grid(row=1, column=1)

send_button = tk.Button(root, text="Send Angles", command=on_send_button_click)
send_button.grid(row=2, column=0, columnspan=2, pady=10)
pickup_button = tk.Button(root, text="Pickup", command=on_pickup_button_click)
pickup_button.grid(row=3, column=0, columnspan=2, pady=5)

drop_button = tk.Button(root, text="Drop", command=on_drop_button_click)
drop_button.grid(row=4, column=0, columnspan=2, pady=5)


# Example usage
if __name__ == "__main__":
    # Start a thread for reading serial debug messages from the Arduino
    read_thread = threading.Thread(target=read_serial)
    read_thread.daemon = True
    read_thread.start()

    root.mainloop()

    # Close the serial port when exiting
    ser.close()