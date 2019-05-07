#! /usr/bin/python3

import socket
import paramiko
import threading
import sys

# using the key from the paramiko demo files

host_key = paramiko.RSAKey(filename='test_rsa.key')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'papa') and (password == 'lovesthepython'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Listening for connection ...')
    client, address = sock.accept()
except Exception as e:
    print('[-] Listen failed:' + e)
    sys.exit(1)
print('[+] Got a connection!')

try:
    bhsession = paramiko.Transport(client)
    bhsession.add_server_key(host_key)
    server = server()
    try:
        bhsession.start_server(server=server)
    except paramiko.SSHException:
        print('[-] SSH negotiation failed.')
    chan = bhsession.accept(20)
    print('[+] Authenticated!')
    print(chan.recv(1024))
    chan.send('Welcome to jb ssh')
    while True:
        try:
            command = input('Enter command: ').strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024) + '\n')
            else:
                chan.send('exit')
                print('exiting!')
                bhsession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhsession.close()
except Exception as e:
    print('[-] Caught an exception: ' + e)

    try:
        bhsession.close()
    except():
        pass
    sys.exit(1)
