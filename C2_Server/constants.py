"""
 File: constants.py
 Description: file where declare constants and global variables
 Designed by: Pasa Larisa

 Module-History:
    2. Add globals for connection between C2 & agents
    1. Add constants for C2 server
"""

# ======================================================================
# CONSTANTS
# ======================================================================
import threading
MUTEX = threading.Lock()
PING_ALERT_MESSAGE = "HELLO "

SERVER_ADDRESS = "10.177.186.2"
SERVER_PORT = 54321

CHECK_WAZUH_STATUS = "wazuh systemctl status wazuh-agent"
ACTIVATE_WAZUH_AGENT = "wazuh sudo systemctl start wazuh-agent"
PREVENTION_STOPPING_AGENT_CHECK = "Active: active (running)"
CHECK_BRUTEFORCE_SSH_SERVICE = "Active: inactive (dead)"


TIMESTAMP_SUBDOCUMENT = "test_latency"
CONSUMPTION_FIELD = "start_consumption"


SCHEDULED_TIME = 30
SCHEDULED_TIMESTP = "seconds"
SCHEDULED_INTERVAL = 30
# ======================================================================
# GLOBALS
# ======================================================================
import queue
ALERTS_QUEUE = queue.Queue()

import logging
logging.basicConfig(filename='server_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

IPS = []
TARGETS = []

STOP_THREADS = False
import socket
C2_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
C2_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)