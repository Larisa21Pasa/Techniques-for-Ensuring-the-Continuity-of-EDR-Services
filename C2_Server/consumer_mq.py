"""
 File: consumer_mq.py
 Description: file which implement consuming from RabbitMq queue and process alerts
 Designed by: Pasa Larisa

 Module-History:
    3. Implement handle function where identify agent and specific action for specific alert
    2. Securely retrieving from rabbitMq queue with mutex + call handle function to process alerts
    1. Create periodically called function for consuming alerts in multithreading way
"""
import datetime
import inspect
import json
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from sqlite3 import IntegrityError

from constants import *
from schedule import every, repeat
from rabbitmq import RabbitMq
from c2 import list_targets, shell
from database_manage import *

RABBIT_MQ = RabbitMq()

def receive_process_alerts_from_rabbitmq():
    """
        Function which call RabbitMq function to retrieve data from queue under mutex threading lock
        and transfer list of alerts for specific agent to process function

        Returns:
        None
   """
    try:
        list_alerts_for_agent = []
        with MUTEX:
            RABBIT_MQ.receive_message()
            if not ALERTS_QUEUE.empty():
                list_alerts_for_agent = ALERTS_QUEUE.get()
                ALERTS_QUEUE.task_done()
        if len(list_alerts_for_agent) != 0:
            handle_agent_alerts(list_alerts_for_agent)

    except Exception as e:
        logging.error(f"[!!][receive_process_alerts_from_rabbitmq()] ERROR when receive data from queue: {e}")
        print(f"[!!][receive_process_alerts_from_rabbitmq()] ERROR when receive data from queue: {e}")


def handle_agent_alerts(list_alerts_for_agent):
    """
        Function which handle alerts for specific agent by type of alert founded

        Returns:
        None
    """
    try:
        pprint(f"*** THREAD[{threading.current_thread().name}] PRIMESTE LISTA: {json.dumps(list_alerts_for_agent,indent=4)} ")
        current_targets = list_targets()
        agent_ip = list_alerts_for_agent[0]["agent"]["ip"]  # A list must contain alerts just for 1 agent
        session = next((session for session, ip in current_targets.items() if ip[0] == agent_ip), None)
        target_socket = TARGETS[session]
        target_ip = IPS[session]
        for alert in list_alerts_for_agent:
            connection = initialize_connection()
            insert_agent(connection, alert['agent']['ip'])
            insert_timestamp(connection,
                             alert['agent']['ip'],
                             alert['test_latency']['start_processing'],
                             alert['test_latency']['start_publishing'],
                             alert['test_latency']['start_consumption']
                             )
            if alert['data']['alert']['signature_id'] == '2001219':
                print("[!!] INFO : SSH Brute Force Detected")
                attacker_ip = alert['data']['src_ip']
                # action - block ip and stop ssh service - shortly attacker should get: Timeout connecting to ip_victim
                bruteforce_ssh_reaction = f"""
                   sudo iptables -A INPUT -s {attacker_ip} -j DROP && \
                   sudo iptables -A OUTPUT -d {attacker_ip} -j DROP && \
                   sudo systemctl stop ssh && \
                   sudo iptables -L -v -n  && \
                   sudo systemctl status ssh &
                   """
                response = shell(target_socket, target_ip, bruteforce_ssh_reaction)
                print(f"C2 Agent has responded:\n************************************************************************\n{response}\n************************************************************************\n")
                if CHECK_BRUTEFORCE_SSH_SERVICE in response:
                    logging.info( f"[++]INFO: Successfully stopped Brute Force Attack for {agent_ip}")
                    print( f"[++]INFO: Successfully stopped Brute Force Attack for {agent_ip}")
                else:
                    logging.info(f"[++]INFO: Unsuccessfully stopped Brute Force Attack for {agent_ip}")
                    print(f"[++]INFO: Unsuccessfully stopped Brute Force Attack for {agent_ip}")

            elif alert['data']['alert']['signature_id'] == '2003068':   # ET SCAN Potential SSH Scan OUTBOUND
                attacker_ip = alert['data']['src_ip']
                bruteforce_ssh_reaction = f" sudo iptables -A OUTPUT -d {attacker_ip} -j DROP & "
                _ = shell(target_socket, target_ip, bruteforce_ssh_reaction)

            else:
                # Generic response for others alerts
                message = f"[{datetime.datetime.now()}] <{agent_ip}> generate : {alert['data']}\n"
                with open('alerts_received.txt', 'a') as file:
                    file.write(message + '\n')
    except IntegrityError as e:
        logging.error(f"IntegrityError occurred: {str(e)}")
        print(f"IntegrityError occurred: {str(e)}")

    except Exception as e:
        logging.error(
            f"[!!][handle_agent_alerts] ERROR when process alerts ( insert timestamp db, treat alerts): {e}")
        print(f"[!!][handle_agent_alerts]  ERROR when process alerts ( insert timestamp db, treat alerts):{e}")


num = 0


@repeat(every(SCHEDULED_INTERVAL).seconds)
def main_consumer():
    global num
    print("CONSUM: ", str(num))
    num += 1
    num_cpus = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=num_cpus) as executor:
        _ = [executor.submit(receive_process_alerts_from_rabbitmq) for _ in range(num_cpus)]
