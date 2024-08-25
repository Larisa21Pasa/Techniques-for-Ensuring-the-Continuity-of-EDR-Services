import json
import multiprocessing
import threading

from schedule import every, repeat

import requests
from concurrent.futures import ThreadPoolExecutor
import time
from mq import RabbitMq

API_URL = "https://jsonplaceholder.typicode.com/posts"
rabbit_mq = RabbitMq()
mutex = threading.Lock()

def fetch_data(url):
    try:
        with mutex:
            response = requests.get(url).json()
            print(f"RESPONSE {threading.current_thread().name}: ", response)
            print("\n\npun in json threadul ", threading.current_thread().name)
            for post in response:
                post["thread_publisher"] = threading.current_thread().name
            message = json.dumps(response)
            rabbit_mq.send_message(message.encode())
        print(f"Datele au fost trimise cu succes de {threading.current_thread().name}.")
    except Exception as e:
        print(f"Eroare la fetch_data: {e}")


@repeat(every(10).seconds)
def main_publisher():
    print("Incep sa trimit")
    num_cpus = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=num_cpus) as executor:
        urls = [API_URL] * 10
        print(f"Thread-ul curent este: {threading.current_thread().name}")
        _ = [executor.submit(fetch_data, url) for url in urls]
