import atexit
import time
from schedule import run_pending

from consumer_mq import *
from rabbitmq import *
from c2 import *
from database_manage import initialize_connection, close_connection

print("**MAIN ")
index = 0
if __name__ == "__main__":
    # initialize_connection()
    # atexit.register(close_connection)
    connection = initialize_connection()
    atexit.register(lambda: close_connection(connection))

    print("TRY TO START SERVER AND LISTENING TH: \n")
    start_server()

    while True:
        # index += 1
        # print("MAIN ", index)
        index = 0 if index > SCHEDULED_TIME else index + 1
        print("Wait ", index, f"/{SCHEDULED_TIME} {SCHEDULED_TIMESTP}\n")
        run_pending()
        time.sleep(1)
