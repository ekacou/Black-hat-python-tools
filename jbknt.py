#! /usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess

# define a few global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


# create the help function
def usage():
    print("JBK Net Tool")
    print()
    print(" Usage: jkbnt.py -t target_host -p port")
    print("-l --listen                  - listen on host [host]:[port] for incoming connection")
    print("-e --execute=file_to_run     - execute the given upon receiving a connection")
    print("-c --command                 - initialize a command shell")
    print("-u --upload=destination      - upon receiving connection upload a file "
          "and write to [destination]")
    print()
    print()
    print("Examples: ")
    print("jbknt.py -t 192.168.124.1 -p 4444 -l -c")
    print("jbknt.py -t 192.168.124.1 -p 4444 -l -u c:\\target.exe")
    print("jbknt.py -t 192.168.124.1 -p 4444 -l -e=\"cat /etc/passwd")
    print("echo 'ABCDEFGHIJ | ./jbknt.py -t 198.122.145.5 -p 741")
    sys.exit(0)


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload from client
    if len(upload_destination):
        # read the entire file then write to the destination
        file_buffer = ""

        # read data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            else:
                file_buffer = + data

        # now lets try to write the file/data to destination
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that the file was writen
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)

        except():
            client_socket.send("Failed to saved file to %s\r\n" % upload_destination)

    # check for command execution
    if len(execute):
        # run the command entered by client
        output = run_command(execute)

        # send the output back to the user
        client_socket.send(output)

    # create a loop if a command shell was requested
    if command:

        while True:

            # show a prompt
            client_socket.send("jbknt:#> ".encode())

            # listen to client until he push enter or until we see a linefeed
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            # send back output to be executed
            response = run_command(cmd_buffer.encode())

            # send back response to user
            client_socket.send(response)


def run_command(command):
    # remove extra characters to the right of the user input
    command = command.rstrip()

    # run the command entered by user/client and get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except():
        output = "Failed to Execute command.\r\n"

    # send the output back to the user/client
    return output


def server_loop():
    global target

    # if no target, listen to all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, address = server.accept()

        # Start a thread to handle our new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


# function to send information read by stdin through the network
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to our target host
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)

        while True:
            # wait for data to come back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break

            print(response, )

            # wait for more input
            buffer = input("")
            buffer += "\n"

            # send the data
            client.send(buffer.encode())
    except():
        print("[*] Exception! Exiting.")

        # tear down the connection
        client.close()


# Create the main function responsible for handling command-line
# arguments and calling the rest of our function
def main():
    global listen
    global port
    global execute
    global command
    global uploadDestination
    global target


# check if the user had entered any arguments following jbknt.py,
#  if nothing was entered by the user, display usage/help
if not len(sys.argv[1:]):
    usage()

# Read the command line options entered by the user
try:
    options, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "port", "target".encode(),
                                                             "command", "upload"])

# if encounters an error, print that error to the screen and display help/usage function
except getopt.GetoptError as err:
    print(str(err))
    usage()

# switch statement to add action to each opts case
for o, a in options:
    if o in ("-h", "--help"):
        usage()
    elif o in ("-l", "--listen"):
        listen = True
    elif o in ("-e", "--execute"):
        execute = a
    elif o in ("-c", "--command"):
        command = True
    elif o in ("-u", "--upload"):
        uploadDestination = a
    elif o in ("-t", "--target"):
        target = a
    elif o in ("-p", "--port"):
        port = int(a)
    else:
        assert False, "Unhandled Option"

# check if jbknettool is supposed to be listening or sending data
if not listen and len(target) and port > 0:
    # read in the buffer from the commandline
    # it will block so send CTRL-D if not sending input to stdin
    buffer = sys.stdin.read()

    # send data off
    client_sender(buffer)

# the tool is going to listen, upload,execute, and drop a shell back
# depending on the commandline option selected by the user
if listen:
    server_loop()

main()
