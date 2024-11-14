import socket
import sys
import os
import time

# if client socket is closed by opposite side - recv returns an empty string
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from file_handler import *

commands = {"get":5,"put":5,"list":4}

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5) #needs a bit of latency
    # will return a socket.timeout error if server cannot be found
    # if Wi-Fi is switched off on client pc we will break with an OSError as it notices Wi-Fi 
    # is manually turned off 
    # in timeout mode (mode we are in) we either break due to a timeout or break due to a system error
    

   # print(f"connecting to {server_address}")


    try:
        client_socket.connect(server_address)
    except OSError:
        raise ConnectionResetError

    print(f"connected to {server_address}")

    return client_socket

def run_command(calls = 5):    
    status_message = "success"
    failure = False
    
    
    try:

        connected_to_server = False
        writing = False

        if command == "list":
            
            client_socket = connect_to_server()
            connected_to_server = True
            send_data(client_socket,command)
            print(recieve_data(client_socket,1024))
        else:
            filename = sys.argv[4]
            if command == "get":
                #early breakout
                if not os.path.isfile(filename): 
                    client_socket = connect_to_server()
                    connected_to_server = True
                    send_data(client_socket,(command+","+filename))
                    response = client_socket.recv(1).decode()
                    if response == "g":
                        writing = True
                        download(client_socket,filename,1024)
                        
                    elif response == "b":
                        raise FileNotFoundError("No such file found in server directory")
                        
                    else: # ""
                        raise ConnectionAbortedError("Connection closed by the other side")
                else:
                    raise FileExistsError("File already exists. Overwrite denied")
            elif command == "put":
                #early breakout
                if os.path.isfile(filename):
                    client_socket = connect_to_server()
                    connected_to_server = True
                    send_data(client_socket,(command+","+filename))

                    response = client_socket.recv(1).decode()
                    if response == "g":
                        upload(client_socket,filename,1024)
                    elif response == "b":
                        raise FileExistsError("File already exists in server directory. Overwrite denied")
                    else:
                        raise ConnectionAbortedError("Connection closed by the other side")
                else:
                    raise FileNotFoundError("No such file found in current working directory")
                
                
    except (ConnectionResetError, socket.timeout,ConnectionAbortedError) as e:

        if writing and os.path.isfile(filename):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
            os.remove(filename)

        if calls == 0:
            status_message = status_message = f"failure -- ServerUnreachable: the maximum number of retry attempts was exceeded"
        else:
            failure = True
            if connected_to_server:
                client_socket.close()
            time.sleep(2) # give server time to get back online
            return run_command(calls-1)

    

    except Exception as e:
        status_message = f"failure -- {get_class_type(e)}: {e}" 

    finally:
        if failure == False:
            if command == "list":
                print(f"({server_ip}, {port_number}): Request {command} -- Status: {status_message}")
            else:
                print(f"({server_ip}, {port_number}): Request {command} on file {filename} -- Status: {status_message}")

            if connected_to_server:
                client_socket.close()
            if status_message != "success":
                exit(1)
            else:
                exit(0)

try:
    server_ip  = sys.argv[1]
    port_number = int(sys.argv[2])
    server_address = ((server_ip,port_number))
    command = sys.argv[3]
    if command not in commands or commands[command] != len(sys.argv) :
       raise ValueError("Input not understood, please put in correct format.") 
    if len(sys.argv) == 5:
        filename = sys.argv[4]
except Exception as e:
    print(f"{get_class_type(e)}: {e}")
    exit(1)
else:
    run_command()
