import time
from schedule import run_pending
from consumer import *

index=0
while True:
    index+=1
    print("MAIN ",index)
    run_pending()
    time.sleep(1)