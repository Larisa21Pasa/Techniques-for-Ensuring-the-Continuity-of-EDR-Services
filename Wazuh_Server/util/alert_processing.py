"""
 File: wazuh_api_client.py
 Description: file which implement all basic function which get important information abou Wazuh
 Designed by: Pasa Larisa

 Module-History:
    2. Added function to get all active agents
    1. Added authentication functions
"""
import datetime
import inspect
import json
import sys
from util.constants import *


def add_timestamp_field(alert, key_name):
    """
    Adds the given key_name with the current timestamp to the 'test_latency' subdocument of the alert.

    Parameters:
    alert (dict): The alert object to update.
    key_name (str): The key name to add in the 'test_latency' subdocument.

    Returns:
    dict: The updated alert object.
    """
    if TIMESTAMP_SUBDOCUMENT not in alert:
        alert[TIMESTAMP_SUBDOCUMENT] = {}
    alert[TIMESTAMP_SUBDOCUMENT][key_name] = datetime.datetime.now()
    return alert

def filter_alert_body(alerts_json):
    # print("filter_alert_body")
    """
       Filters the body of alerts JSON.

       Args:
           alerts_json (str): JSON string containing alerts.

       Returns:
           str: JSON string containing filtered alerts.
    """
    try:
        simplified_alerts = []
        if not alerts_json:
            logging.error(f"[**][filter_alert_body()] INFO: No alerts JSON data provided.")
            print(f"[**][filter_alert_body()] INFO: No alerts JSON data provided.")
            return []

        try:
            alerts = json.loads(alerts_json)
        except json.JSONDecodeError as e:
            logging.error(f"[!!][filter_alert_body()] ERROR JSON decoding error: {e}")
            print(f"[!!][filter_alert_body()] ERROR JSON decoding error: {e}")
            return []

        def filter_recursive(original, structure):
            simplified = {}
            # Iterate over the keys and values in the filter structure
            for key, value in structure.items():
                # If the value is a dictionary, recursively filter the original alert
                if isinstance(value, dict):
                    if key in original and isinstance(original[key], dict):
                        simplified[key] = filter_recursive(original[key], value)

                # If the key exists in the original alert and matches the filter, ignore the alert
                elif key in original and original[key] == FILTER_ON_CATEGORY_FIELD.get(key):
                    return {}

                # If the key exists in the original alert, include it in the simplified alert
                elif key in original:
                    simplified[key] = original[key]

            # If there is an empty entry, the alert is ignored
            if {} in simplified.values():
                return {}
            else:
                return simplified

        for alert in alerts:
            # Filter the data and agent fields of the alert and create a simplified alert
            simplified_alert = {
                'test_latency': {PROCESSING_FIELD : str(datetime.datetime.now())},
                'data': filter_recursive(alert.get('data', {}), ALERT_BODY.get('data', {})),
                'agent': filter_recursive(alert.get('agent', {}), ALERT_BODY.get('agent', {}))
            }
            # timestamp for publishing is saved in rabbit.py: send_message()
            simplified_alerts.append(simplified_alert)
        return simplified_alerts

    except json.JSONDecodeError as e:
        logging.error(f"[!!][filter_alert_body()] ERROR JSON decoding error: {e}")
        print(f"[!!][filter_alert_body()] ERROR JSON decoding error: {e}")
        sys.exit(1)

    except KeyError as e:
        logging.error(f"[!!][filter_alert_body()] ERROR Key error:{e}")
        print(f"[!!][filter_alert_body()] ERROR Key error:{e}")
        sys.exit(1)

    except Exception as e:
        logging.error(f"[!!][filter_alert_body()] ERROR - unknown: {e}")
        print(f"[!!][filter_alert_body()] ERROR - unknown: {e}")
        sys.exit(1)
