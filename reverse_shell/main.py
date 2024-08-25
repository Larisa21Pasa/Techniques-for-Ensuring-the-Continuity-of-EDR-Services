# !/usr/bin/python

import socket
from termcolor import colored

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(("192.168.100.5", 54321))
s.listen(5)

print(colored("[+] Listening For Incoming connecions"))

target, ip = s.accept()
print(colored("[+] Connection established from %s " % str(ip)))