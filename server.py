import socket
import threading

# create a socket for the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12001))

# start listening for connections
server.listen()

# lists to keep track of clients and their usernames
clients = []
usernames = []
user_connections = {}

def broadcast(message, sender=None):
    # decode the message from bytes to string
    message = message.decode('ascii')
    if message.startswith('@'):
        # handles unicast messages
        recipient = message.split()[0][1:]
        msg = message.split(' ', 1)[1]
        if recipient in user_connections:
            # sends message to the chosen recipient
            user_connections[recipient].send(f'{usernames[clients.index(sender)]}: {msg}'.encode('ascii'))
            if sender:
                # sends a confirmation of the message to the sender
                sender.send(f'You to {recipient}: {msg}'.encode('ascii'))
    else:
        # handles broadcast messages
        for client in clients:
            if client != sender:
                client.send(message.encode('ascii'))

def handle(client):
    while True:
        try:
            # receive messages from the client
            message = client.recv(1024)
            if message.decode('ascii').startswith('@'):
                # broadcast unicast messages
                broadcast(message, client)
            else:
                # broadcast the message to all clients
                broadcast(message, client)
        except:
            # remove the client if an error occurs
            index = clients.index(client)
            # remove the client and close the connection
            clients.remove(client)
            client.close()
            # get the username of the client
            username = usernames[index]
            # broadcast that the client has left
            broadcast(f'{username} has left'.encode('ascii'))
            # remove the username from the list
            usernames.remove(username)
            # remove the connection from the dictionary
            del user_connections[username]
            break

def receive():
    while True:
        # accept new client connections
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # send a message to the client to choose a username
        client.send('NICK'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        # add the username and client to the lists
        usernames.append(username)
        clients.append(client)
        user_connections[username] = client

        
        print(f'Username of the client is {username}')
        # broadcast that the client has joined
        broadcast(f'{username} joined the chat!'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        # create a thread for the new client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()