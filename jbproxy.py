#! /usr/bin/python3

import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))

    except():
        print('[!!] Failed to listen on %s:%d' % (local_host, local_port))
        print("[!!] Check for other listening socket or correct permission.")
        sys.exit(0)

    print('[*] Listening on %s:%d' % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, address = server.accept()

        # print out local connection information
        print("[==>] Received incoming connection from $s:%d" % (address[0], address[1]))

        # start a thread to talk to the remote host
        proxy_threat = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))

        proxy_threat.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to the host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # sent it to the response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to our local client, send it
        if len(remote_buffer):
            print("[<==] sending %d bytes to local host." % len(remote_buffer))
            client_socket.send(remote_buffer)

    # loop and read from local, send to remote,  send to local and repeat
    while True:

        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] received %d bytes to localhost" % len(local_buffer))
            hexdump(local_buffer)

            # send it to the request_handler
            localbuffer = request_handler(local_buffer)

            # send the data to the remote host
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        # receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)

            # send to our response handler
            remote_buffer = response_handler(remote_buffer)

            # send the response to the local socket
            client_socket.send(remote_buffer)

            print("[<==] Sent to localhost.")

        # if not more data needs to be transmitted on either side, close the connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()

            print("[*] No more data. Closing connections.")

            break


# this is an hex dumping function

def hexdump(src, lenght=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), lenght):
        s = src[i:i + lenght]
        hex = b''.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, lenght * (digits + 1), hex, text))

        print(b'\n'.join(result))


def receive_from(connection):
    buffer = ""

    # lets set a 2 second timeout; depending on your target, this may be adjusted
    connection.settimeout(2)

    try:
        # keep reading data until no more data or until we timeout
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data

    except():
        pass

    return buffer


# modify any requests destined for the remote host

def request_handler(buffer):
    # perform packet modifications
    return buffer


# modify any responses destined to the local host
def response_handler(buffer):
    # perform packet modification
    return buffer


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./jbkProxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("example: ./jbkProxy.py 127.0.0.01 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target parameters
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # tell the proxy to connect and receive data before sending anything
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # now lets setup the listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


main()
