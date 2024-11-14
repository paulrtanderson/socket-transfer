import socket
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from file_handler import *



def read_socket(client_socket):
    data = recieve_data(client_socket,1024)
    client_arguments = data.split(",",1)
    command = client_arguments[0]
    commands = {"get":2,"put":2,"list":1}
    if command not in commands or commands[command] != len(client_arguments):
        raise ValueError("Client arguments not valid. Suspicious activity detected. Connection closed")
    return client_arguments

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port_number = int(sys.argv[1])

try:
    server_socket.bind(("",port_number))
    server_socket.listen(5)
except Exception as e:
    # in the case that the port is already in use
    print(f"{get_class_type(e)}: {e}")
    exit(1)
else:
    print(f"({ip_address}, {port_number}): server up and running")

while True:
    status_message = "success"
    writing = False
    malicious = False
    try:
        print("waiting for a new connection")
        client_socket, client_address = server_socket.accept()
        # client_socket.settimeout(2) - not needed - timeout is inherited from accept
        client_ip, client_port_number = client_address
        client_arguments = read_socket(client_socket)

        command = client_arguments[0]
        if command == "list":
            files = "\n".join(os.listdir())
            send_data(client_socket,files)


        else:
            filename = str(client_arguments[1])

            if command == "get":
                if os.path.isfile(filename):
                    client_socket.sendall("g".encode())
                else:
                    client_socket.sendall("b".encode())
                    raise FileNotFoundError("No such file found. Client request denied.")
                upload(client_socket,filename,1024)
    

            elif command == "put":
                if not os.path.isfile(filename):
                    client_socket.sendall("g".encode())
                else:
                    client_socket.sendall("b".encode())
                    raise FileExistsError("File already exists. Overwrite denied")
                writing = True
                download(client_socket,filename,1024)
                
    except ValueError as e:
        malicious = True
        print({get_class_type(e): e})
            
    except Exception as e:

        status_message = f"failure -- {get_class_type(e)}: {e}" 
        if writing and os.path.isfile(filename):
            os.remove(filename)
        


    finally:
        if malicious == False:
            print(status_message)
            if command == "list":
                print(f"({client_ip}, {client_port_number}): Request {command} -- Status: {status_message}")
            else:
                print(f"({client_ip}, {client_port_number}): Request {command} on file {filename} -- Status: {status_message}")

        
        
        client_socket.close()