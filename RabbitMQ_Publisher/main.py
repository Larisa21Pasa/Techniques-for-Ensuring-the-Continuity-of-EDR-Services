# import json
# import multiprocessing
# import threading
#
# from schedule import every, repeat
#
# import requests
# from concurrent.futures import ThreadPoolExecutor
# import time
# from mq import RabbitMq
#
# API_URL = "https://jsonplaceholder.typicode.com/posts"
# rabbit_mq = RabbitMq()
#
# def fetch_data():
#     try:
#         response = requests.get(API_URL).json()
#         message = json.dumps(response)  # Converteste răspunsul în șir de caractere JSON
#         rabbit_mq.send_message(message.encode())  # Trimite mesajul ca bytes-like object
#         print("Datele au fost trimise cu succes.")
#     except Exception as e:
#         print(f"Eroare la fetch_data: {e}")
#
# @repeat(every(10).seconds)
# def main_publisher():
#     num_cpus = multiprocessing.cpu_count()
#     with ThreadPoolExecutor(max_workers=num_cpus) as executor:
#         print(f"Thread-ul curent este: {threading.current_thread().name}")
#
#         executor.submit(fetch_data)
import time

from schedule import run_pending

from publisher import *

index=0

while True:
    index+=1
    print("MAIN ",index)
    run_pending()
    time.sleep(1)


