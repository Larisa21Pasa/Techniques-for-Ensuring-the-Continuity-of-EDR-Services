"""
 File: wazuh_api_client.py
 Description: file which implement all basic function which get important information abou Wazuh
 Designed by: Pasa Larisa

 Module-History:
    2. Added function to get all active agents
    1. Added authentication functions
"""
import json
from base64 import b64encode
from functools import wraps
import sys
import requests
from util.constants import *
import inspect
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #for demo, it is not necesary to get wazuh certificate```
frame = inspect.currentframe()
filename = inspect.getframeinfo(frame).filename


# ======================================================================
# WAZUH UTILS
# ======================================================================
def authenticate(func):
    """
      Decorator for authentication.

      This decorator adds authentication functionality to a function by checking if
      a JWT token is provided as a keyword argument. If not, it performs authentication
      and adds the token to the function's keyword arguments.

      Args:
          func: The function to be decorated.

      Returns:
          The decorated function.
      """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # If not received token, then autnetication starts
        if 'token' not in kwargs:
            token = authenticate_and_get_token()
            kwargs['token'] = token

        # Original function call
        return func(*args, **kwargs)

    return wrapper


def authenticate_and_get_token():
    """
        Authenticates the user and retrieves the JWT token.

        Returns:
            The JWT token if authentication is successful, None otherwise.
    """
    global frame, filename
    funcname = inspect.getframeinfo(frame).function

    login_url = f"{PROTOCOL}://{WAZUH_HOST}:{WAZUH_PORT}/{WAZUH_LOGIN_ENDPOINT}"
    basic_auth = f"{WAZUH_USER}:{WAZUH_PASSWORD}".encode()
    login_headers = {'Content-Type': 'application/json',
                     'Authorization': f'Basic {b64encode(basic_auth).decode()}'}

    print("\nLogin request ...\n")
    try:
        response = requests.post(login_url, headers=login_headers, verify=False)
        response.raise_for_status()
        token = json.loads(response.content.decode())['data']['token']
    except requests.exceptions.RequestException as e:
        logging.error(f"[!!][{filename}][{funcname}] ERROR during authentication:  {e}")
        print(f"[!!][{filename}][{funcname}] ERROR during authentication: {e}")
        sys.exit(1)
    return token


@authenticate
def get_all_agents(*, token=None):
    """
    Retrieve a list of all Wazuh agents' IDs using the Wazuh API.

    Args:
        token: The JWT authentication token obtained earlier.

    Returns:
        A list with the IDs of the agents, or None in case of an error.
    """
    global frame, filename
    funcname = inspect.getframeinfo(frame).function

    url = f"{PROTOCOL}://{WAZUH_HOST}:{WAZUH_PORT}/{LIST_AGENTS_IDS_QUERY}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        # Send a GET request to the Wazuh API endpoint
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        agent_ids = response.json().get("data", {}).get("affected_items", [])

        # Filter out any agent ID equal to "000"
        filtered_agent_ids = [agent["id"] for agent in agent_ids if agent["id"] != "000"]
        print("agent_ids = ", filtered_agent_ids)
        return filtered_agent_ids

    except requests.exceptions.RequestException as e:
        # If an error occurs during the request, print the error message
        logging.error(f"[!!][{filename}][{funcname}] ERROR while getting agents list: {e}")
        print(f"[!!][{filename}][{funcname}] ERROR while getting agents list: {e}")
        sys.exit(1)
