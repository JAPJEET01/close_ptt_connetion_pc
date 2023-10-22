import socket
import pyaudio
import threading
import tkinter as tk

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345     # Port for sender
RECEIVER_IP = '192.168.29.157'  # Receiver's IP address
RECEIVER_PORT = 12346   # Port for receiver
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet
server_ip = '192.168.29.157'  # Raspberry Pi's IP address
server_port = 12356

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((SENDER_HOST, RECEIVER_PORT))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ptt_active = False

def send_audio():
    while True:
        if ptt_active:
            data = sender_stream.read(CHUNK)
            for i in range(0, len(data), MAX_PACKET_SIZE):
                chunk = data[i:i+MAX_PACKET_SIZE]
                sender_socket.sendto(chunk, (RECEIVER_IP, RECEIVER_PORT))

def receive_audio():
    while True:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_thread = threading.Thread(target=receive_audio)
sender_thread.start()
receiver_thread.start()

#  Create a function to draw a red circle for "Busy" status
def draw_busy_circle():
    canvas.create_oval(100, 100, 200, 200, fill="red")
    canvas.create_text(150, 150, text="Busy", fill="white" ,font=("Helvetica", 18, "bold"))

# Create a function to draw a blue circle for "Ready to Use" status
def draw_ready_circle():
    canvas.create_oval(100, 100, 200, 200, fill="blue")
    canvas.create_text(150, 150, text="Available",  fill="white", font=("Helvetica", 16, "bold"))

# Create a function to simulate key press
def simulate_key_press():
    client_socket.sendto(b'high', (server_ip, server_port))
    global ptt_active
    ptt_active = True
    status_label.config(text="Status: Talking", fg="blue")
    print("Talking")
    canvas.delete("all")  # Clear the canvas
    draw_busy_circle()

# Create a function to simulate key release
def simulate_key_release():
    client_socket.sendto(b'low', (server_ip, server_port))
    global ptt_active
    ptt_active = False
    status_label.config(text="Status: Not Talking", fg="red")
    print("Not Talking")
    canvas.delete("all")  # Clear the canvas
    draw_ready_circle()

def key_pressed(event):
    if event.keysym == 'p':
        client_socket.sendto(b'high', (server_ip, server_port))
    global ptt_active
    if event.keysym == 'p':
        ptt_active = True
        print("Talking...")

def key_released(event):
    if event.keysym == 't':
        client_socket.sendto(b'low', (server_ip, server_port))

    global ptt_active
    if event.keysym == 't':
        ptt_active = False
        print("Not talking...")


# Create the main window
root = tk.Tk()
root.title("PTT Control")
root.geometry("440x440")  # Set a square window size
# root.configure(bg="black")
# Create buttons for key press and key release
key_press_button = tk.Button(root, text="Key Press (P)", command=simulate_key_press, bg="blue", padx=10, pady=10)
key_release_button = tk.Button(root, text="Key Release (T)", command=simulate_key_release, bg="red", padx=10, pady=10)

# Create a label for the status
status_label = tk.Label(root, text="Status: Not Talking", font=("Helvetica", 21, "bold"))

# Create a canvas for drawing circles
canvas = tk.Canvas(root, width=300, height=300)

# Pack the elements to display them in the window
key_press_button.pack(pady=10)
key_release_button.pack(pady=10)
status_label.pack()
canvas.pack()

# Initialize the canvas with a blue circle for "Ready to Use"
draw_ready_circle()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
# Start the Tkinter main loop
root.mainloop()
