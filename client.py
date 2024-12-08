import socket
import threading
import sys

# get the username, hostname, and port number from the command line arguments
if len(sys.argv) != 4:
    print("Usage: python3 client.py <username> <hostname> <port>")
    sys.exit(1)

username = sys.argv[1]
hostname = sys.argv[2]
port = int(sys.argv[3])

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
# connect to the server
client.connect((hostname, port))

def receive():
    while True:
        try:
            # receive messages from the server
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                # send the username to the server
                client.send(username.encode('ascii'))
            else:
                # print the message
                print(message)
        except:
            # close the connection if an error occurs
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        # get user input for the message
        message = input("")
        if message.startswith('@'):
            # send unicast message if it starts with '@'
            client.send(message.encode('ascii'))
        else:
            client.send(f'{username}: {message}'.encode('ascii'))

# create two threads for receiving and writing messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)  
write_thread.start()