#! /usr/bin/python3

import threading
import paramiko
import subprocess


def ssh_command(ip, user, passwd, command):
    Client = paramiko.SSHClient()
    # client.load_host_keys('/home/papa/ .ssh/know_host')
    Client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    Client.connect(ip, username=user, password=passwd)
    ssh_Session = Client.get_transport().open_session()
    if ssh_Session.active:
        ssh_Session.exsc_command(command)
        print(ssh_Session.recv(1024))
    return


ssh_command('192.168.0.111', 'test', 'motdepass', 'ip')
