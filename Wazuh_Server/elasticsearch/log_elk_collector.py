"""
 File: log_elk_collector.py
 Description: file for collects alerts and process them
 Designed by: Pasa Larisa

 Module-History:
    3.
    2. Implement request function which takes alerts from ELK API
    1. Added scheduled function which implement a ThreadPoolExecutor to multithreading-process periodically alerts
"""
import datetime
from concurrent.futures import ThreadPoolExecutor
from wazuh.wazuh_api_client import *
import requests
from schedule import every, repeat
import multiprocessing
from util.alert_processing import *
from util.constants import *


# ======================================================================
# LOG COLLLECTOR UTILS
# ======================================================================
def generate_elk_query(agent_id, rule_groups, time_range_start, time_range_end, page_size, sort_field, sort_order):
    """
       Generates an Elasticsearch query based on the provided parameters.

       Args:
           agent_id (str): The ID of the agent to filter the logs for.
           rule_groups (str): The rule groups to filter the logs by.
           time_range_start (str): The start of the time range for filtering logs.
           time_range_end (str): The end of the time range for filtering logs.
           page_size (int): The number of logs to return per page.
           sort_field (str): The field to sort the logs by.
           sort_order (str): The order in which to sort the logs ('asc' for ascending, 'desc' for descending).

       Returns:
           dict: The Elasticsearch query request.
       """
    query = {
        "bool": {
            "must": [
                {
                    "term": {
                        "agent.id": agent_id
                    }
                },
                {
                    "term": {
                        "rule.groups": rule_groups
                    }
                },
                {
                    "range": {
                        "@timestamp": {
                            "gte": time_range_start,
                            "lte": time_range_end
                        }
                    }
                }
            ]
        }
    }

    request = {
        "query": query,
        "size": page_size,
        "sort": {
            sort_field: {
                "order": sort_order
            }
        }
    }
    return request


def get_suricata_alerts_last_scheduled_interval(agent_id):
    # print("get_suricata_alerts_last_30m")
    """
       Retrieves Suricata alerts for the last 30 minutes for a specified agent.

       Args:
           agent_id (str): The ID of the agent to fetch alerts for.
       Returns:
           str: JSON string containing the extracted Suricata alerts.
    """
    query = generate_elk_query(
        agent_id=agent_id,
        rule_groups=QUERY_RULE_GROUPS,
        time_range_start=QUERY_TIME_RANGE_START,
        time_range_end=QUERY_TIME_RANGE_END,
        page_size=QUERY_PAGE_SIZE,
        sort_field=QUERY_SORT_FIELD_TIMESTAMP,
        sort_order=QUERY_SORT_ORDER_DESC
    )
    try:
        response = requests.get(
            f"{URL_ELASTICSEARCH}/{INDEX_NAME}/_search",
            verify=SSL_CERTIFICATE_PATH,
            auth=ELK_AUTH,
            headers={"Content-Type": "application/json"},
            data=json.dumps(query)
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"[!!][get_suricata_alerts_last_30m(agent_id)] ERROR fetching alerts for agent {agent_id}: {e}")
        print(f"[!!][get_suricata_alerts_last_30m(agent_id)] ERROR fetching alerts for agent {agent_id}: {e}")
        return []

    # get from full response just information about alerts
    alerts = json.loads(response.content)["hits"]["hits"]
    total_alerts = json.loads(response.content)["hits"]["total"]["value"]
    if total_alerts > 0:
        extracted_data = []
        for alert in alerts:
            data_agent_values = {
                "data": alert["_source"]["data"],
                "agent": alert["_source"]["agent"]
            }
            extracted_data.append(data_agent_values)
        extracted_data = json.dumps(extracted_data, indent=4)
        print(f"Brute alerts without proccessing: \n************************************************************************\n{extracted_data}\n************************************************************************\n")
        return extracted_data
    else:
        # In case if there is no alerts
        return []


def publish_to_rabbitmq(formatted_alerts):
    """
          Create a thread-lock object to safely publish alerts to RabbitMq queue

          Args:
              formatted_alerts (list): List with alerts for specific agent
          Returns:
            None
    """
    try:
        with MUTEX:
            RABBITMQ_OBJECT.send_message(formatted_alerts)

        logging.info(f"[++][publish_to_rabbitmq(formatted_alerts)] INFO: Successfully published alerts at [{datetime.datetime.now()}]")
        print(f"[++][publish_to_rabbitmq(formatted_alerts)] INFO: Successfully published alerts at [{datetime.datetime.now()}]")
    except Exception as e:
        logging.error(f"[!!][publish_to_rabbitmq(formatted_alerts)] ERROR when try to publish alerts: {e}")
        print(f"[!!][publish_to_rabbitmq(formatted_alerts)] ERROR when try to publish alerts: {e}")


def process_agent_alerts(agent_id):
    """
         Central function where the logical flow is orchestrated. Target function for threads
                - each agent has assigned specific thread
         Args:
             agent_id (str): String with id of agent
         Returns:
           None
    """
    logging.info(f"[++][process_agent_alerts(agent_id)] INFO: Start procees alerts for agent [{str(agent_id)}]")
    print( f"[++][process_agent_alerts(agent_id)] INFO: Start procees alerts for agent [{str(agent_id)}]")
    try:
        alerts = get_suricata_alerts_last_scheduled_interval(agent_id)
        if alerts:
            formatted_alerts = filter_alert_body(alerts)
            publish_to_rabbitmq(formatted_alerts)

    except Exception as e:
        logging.error(f"[!!][process_agent_alerts(agent_id)] ERROR when collection alerts for agent {agent_id}: {e}")
        print(f"[!!][process_agent_alerts(agent_id)] ERROR when collection alerts for agent {agent_id}: {e}")



@repeat(every(SCHEDULED_INTERVAL).seconds)
def collect_and_send_alerts():
    """
       Function to collect and send alerts from all agents at regular intervals.

       This function retrieves a list of all agents, then processes alerts from each agent concurrently using a
       ThreadPoolExecutor. The number of worker threads is determined based on the number of available CPU cores.

       The alerts are processed asynchronously, and the function returns once all alerts have been processed.

       Note: This function is intended to be used as a periodic task to continuously collect and send alerts from all agents.

       Returns:
           None
       """
    agent_ids = get_all_agents()
    num_cpus = multiprocessing.cpu_count()

    with ThreadPoolExecutor(max_workers=num_cpus) as executor:
        _ = [executor.submit(process_agent_alerts, agent_id) for agent_id in agent_ids]
