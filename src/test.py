
import socket

 

# A TCP based echo server

echoSocket = socket.socket()

# Bind the IP address and the port number

echoSocket.bind(("192.168.194.60", 5060)) 

 

# Listen for incoming connections

echoSocket.listen(1) 

 

# Start accepting client connections

while(True):

    (clientSocket, clientAddress) = echoSocket.accept() 

   

    # Handle one request from client

    while(True):

        data = clientSocket.recv(1024) 

        print("At Server: %s"%data) 

 

        if(data!=b''):

            # Send back what you received

            clientSocket.send(data) 

            break 