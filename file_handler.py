import os
import socket
import sys
import time


def download(client_socket,filename,chunk_size):
    expected_bytes = client_socket.recv(chunk_size).decode()
    if expected_bytes == "":
        raise ConnectionAbortedError("Connection closed by the other side")
    expected_bytes = int(expected_bytes)
    client_socket.sendall("g".encode()) # g for go/good

    

    with open(file=filename,mode="xb") as f:
        bytes_read = 0
        non_empty_chunk = True
        
        # will not hang forever as we have a timeout set
        while bytes_read < expected_bytes and non_empty_chunk:

            chunk = client_socket.recv(chunk_size)
            f.write(chunk)
            bytes_read += len(chunk)
            if len(chunk) == 0:
                non_empty_chunk = False

        if non_empty_chunk == False:
            raise ConnectionAbortedError("Connection closed by the other side")
    
        print("finished writing")

def upload(client_socket,filename,chunk_size):
    with open(file=filename,mode="rb") as f: 
        expected_bytes = os.path.getsize(filename) 
        client_socket.sendall(str(expected_bytes).encode("utf-8"))# integer -> str so we can encode

        client_socket.recv(1).decode() # if it gets any response we are good to go
        # could get "" here if connection aborted but sendall will timeout
       
        bytes_read = 0
        while bytes_read < expected_bytes:
            chunk = f.read(chunk_size) 
            client_socket.sendall(chunk)
            bytes_read += chunk_size

def send_data(client_socket,message):
    expected_bytes = len(message.encode())
    client_socket.sendall(str(expected_bytes).encode())

    response = client_socket.recv(1).decode() # if it gets any response we are good to go
    # could get "" here if connection aborted but sendall will timeout
    
    client_socket.sendall(message.encode())

def recieve_data(client_socket,chunk_size):
    expected_bytes = client_socket.recv(1024).decode("utf-8")

    if expected_bytes == "":
        raise ConnectionAbortedError("Socket closed by other side")
    
    expected_bytes = int(expected_bytes)
    
    client_socket.sendall("g".encode()) # g for go/good

    bytes_recieved = 0
    data  = ""
    non_empty_chunk = True
    while bytes_recieved < expected_bytes and non_empty_chunk:
        chunk = client_socket.recv(chunk_size)
        data += chunk.decode()
        bytes_recieved += len(chunk)
        if len(chunk) == 0:
            non_empty_chunk = False

    if non_empty_chunk == False:
        raise ConnectionAbortedError("Socket closed by the other side")

    if bytes_recieved != expected_bytes: 
        raise ValueError("too much data sent")
    
    return data

def get_class_type(error_obj):
    t = str(type(error_obj))
    t = t.split("'")
    return t[1]
