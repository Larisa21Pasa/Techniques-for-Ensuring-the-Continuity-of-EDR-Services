"""
 File: main.py
 Description: file which start the program
 Designed by: Pasa Larisa

 Module-History:
    1. Added run_pending() which executes any scheduled tasks that are due to run -> collect_and_send_alerts to every x time
"""
import concurrent.futures
import time
import requests
from schedule import every, repeat, run_pending
import json
from datetime import datetime
from util.constants import *
from elasticsearch.log_elk_collector import *
from util.alert_processing import  *

index = 0
while True:
    index = 0 if index > SCHEDULED_TIME else index + 1
    print("Wait ", index, f"/{SCHEDULED_TIME} {SCHEDULED_TIMESTP}\n")
    run_pending()
    time.sleep(1)
