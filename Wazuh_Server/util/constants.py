"""
 File: constants.py
 Description: file for declare all constant variables
 Designed by: Pasa Larisa

 Module-History:
    1. Add constants
"""
PROTOCOL = "https"
# ======================================================================
# LOG COLLECTOR CONSTANTS
# ======================================================================
URL_ELASTICSEARCH = "https://10.177.186.2:9200"
SSL_CERTIFICATE_PATH = "/Users/adim/Desktop/FACULTATE/LICENTA/ELASTICSEARCH/elasticsearch-8.12.2/config/certs/http_ca.crt"  # path to be changed accordingly


ELK_AUTH = ("elastic", "7-0PzJB2iP4D-ZsJvJdI") # credentials from install elk process
VERIFY_CERTS = False
INDEX_NAME = "wazuh-alerts*"

QUERY_RULE_GROUPS = "suricata"
# QUERY_TIME_RANGE_START = "now-30m"
QUERY_TIME_RANGE_START = "now-60s"
QUERY_TIME_RANGE_END = "now"
QUERY_PAGE_SIZE = 10
QUERY_SORT_FIELD_TIMESTAMP = "@timestamp"
QUERY_SORT_ORDER_DESC = "desc"
SCHEDULED_TIME = 60
SCHEDULED_TIMESTP = "seconds"
# ======================================================================
# WAZUH CONSTANTS
# ======================================================================
WAZUH_HOST = '10.177.186.3'
WAZUH_PORT = 55000
WAZUH_USER = 'wazuh'
WAZUH_PASSWORD = 'wazuh'
WAZUH_LOGIN_ENDPOINT = 'security/user/authenticate'
LIST_AGENTS_IDS_QUERY = "agents?select=id"

import logging
logging.basicConfig(filename='error_app_log.log', level=logging.ERROR, format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

# ======================================================================
# SURICATA CONSTANTS
# ======================================================================

ALERT_BODY = {
    "data": {
        "dest_ip": None,
        "timestamp": None,
        "dest_port": None,
        "src_port": None,
        "src_ip": None,
        "proto": None,
        "event_type": None,
        "alert": {
            "signature_id": None,
            "action": None,
            "severity": None,
            "signature": None,
            "category": None
        }
    },
    "agent": {
        "id": None,
        "name": None,
        "ip": None
    },
    "test_latency": {

    },
}

# FILTER_ON_CATEGORY_FIELD = {"category": "Not Suspicious Traffic"}
FILTER_ON_CATEGORY_FIELD = {"category": "Not"}

TIMESTAMP_SUBDOCUMENT = "test_latency"
PROCESSING_FIELD = "start_processing"
PUBLISHING_FIELD = "start_publishing"
CONSUMPTION_FIELD = "start_consumption"

# ======================================================================
# RABBIT MQ CONSTANTS
# ======================================================================
import threading
from rabbitmq.rabbit import RabbitMq

RABBITMQ_OBJECT = RabbitMq()
MUTEX = threading.Lock()
SCHEDULED_INTERVAL = 60