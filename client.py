import socket
import threading
import sys
import os

# get the username, hostname, and port number from the command line arguments
if len(sys.argv) != 4:
    print("Usage: python3 client.py <username> <hostname> <port>")
    sys.exit(1)

username = sys.argv[1]
hostname = sys.argv[2]
port = int(sys.argv[3])

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
try:
    # connect to the server
    client.connect((hostname, port))
except socket.gaierror:
    print(f"Error: Hostname '{hostname}' is unavailable. Please check the hostname and try again.")
    sys.exit(1)
except ConnectionRefusedError:
    print(f"Error: Connection to {hostname} on port {port} refused. Please check the port and try again.")
    sys.exit(1)

is_quitting = False
def receive():
    # use the global variable is_quitting to indicate if the user is leaving
    global is_quitting
    while True:
        try:
            # receive messages from the server
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                # send the username to the server
                client.send(username.encode('ascii'))
            elif message == '/quit':
                # Thank the user for using the server
                print('Goodbye! Come again soon.')
                client.close()
            else:
                # print the message
                print(message)
        except:
            if not is_quitting:    
                # close the connection if an error occurs
                print("An error occurred!")
                client.close()
            break

def write():
    global is_quitting
    while True:
        # get user input for the message
        message = input("")
        if message.startswith('@'):
            # send unicast message if it starts with '@'
            client.send(message.encode('ascii'))
        elif message == "/quit":
            # send a message to the server indicating the user is leaving
            client.send(f'{username} has left'.encode('ascii'))
            is_quitting = True
            client.close()
            break
        # prevent user from sending empty messages
        elif message == "":
            continue
        elif message == 'LIST_FILES':
            client.send(message.encode('ascii'))
        elif message.startswith('DOWNLOAD_FILE'):
            client.send(message.encode('ascii'))
            filename = message.split(' ')[1]
            response = client.recv(1024).decode('ascii')
            if response.startswith('FILE_SIZE'):
                filesize = int(response.split(' ')[1])
                os.makedirs(username, exist_ok=True)
                filepath = os.path.join(username, filename)
                with open(filepath, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = client.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                print(f"Downloaded {filename} ({filesize} bytes)")
            else:
                print(response)
            
        else:
            # send broadcast message
            client.send(f'{username}: {message}'.encode('ascii'))

# create two threads for receiving and writing messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)  
write_thread.start()