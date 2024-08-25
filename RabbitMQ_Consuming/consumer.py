import json
import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from mq import RabbitMq
from schedule import every, repeat

rabbit_mq = RabbitMq()
mutex = threading.Lock()

def receive_data():
    print("receive_data()")
    try:
        print("in try")
        with mutex:
            message = rabbit_mq.receive_message()
            print(" message = rabbit_mq.receive_message() ", message)
    except Exception as e:
        print(f"Eroare la receive_data: {e}")

@repeat(every(10).seconds)
def main_consumer():
    print("Incep sa consum...")
    num_cpus = multiprocessing.cpu_count()
    print("main_consumer()")
    with ThreadPoolExecutor(max_workers=num_cpus) as executor:
        _ = [executor.submit(receive_data) for _ in range(num_cpus)]
