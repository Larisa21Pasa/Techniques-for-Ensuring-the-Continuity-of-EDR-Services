"""
 File: database_manage.py
 Description: file which implement CRUD on timestamps for agents
 Designed by: Pasa Larisa

 Module-History:
    2. Added insert function for agents and their timestamps
    1. Added initialize function which is called in each thread
"""
import sqlite3
DB_PATH = 'c2_server.db'


def initialize_connection():
    """
           Function which initialize sqlite3 database

           Returns:
           connection  - connection created
      """
    try:
        connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        # print("[+] Successfully connected to database")
        return connection
    except sqlite3.DatabaseError as e:
        print(f"[!!] ERROR connecting to database: {e}")
        return None


def close_connection(connection):
    """
           Function which close connection when program is closed ( used atexit)

           Returns:
           None
      """
    if connection:
        try:
            connection.close()
            print("[+] Successfully closed connection to database")
        except sqlite3.DatabaseError as e:
            print(f"[!!] ERROR closing the database: {e}")




def insert_agent(connection, ip):
    """
           Insert agent in table if not exists

           Returns:
           None
      """
    if connection is None:
        print("[!!] ERROR: Database connection is not initialized")
        return

    cursor = connection.cursor()
    try:
        cursor.execute('INSERT INTO AGENTS (ip) VALUES (?)', (ip,))
        connection.commit()
        print("[+] INFO: Agent inserted successfully.")

    except sqlite3.DatabaseError as e:
        if "UNIQUE" in str(e):
            pass
        else:
            print(f"[!!] ERROR inserting agent to database: {e}")
    finally:
        cursor.close()


def insert_timestamp(connection, ip, start_processing, start_publishing, start_consumption):
    """
       Insert timestamps for agent in table

       Returns:
       None
  """
    if connection is None:
        print("[!!] ERROR: Database connection is not initialized")
        return
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT id FROM AGENTS WHERE ip = ?', (ip,))
        result = cursor.fetchone()
        if result is None:
            print(f"[!!] ERROR: Agent with IP {ip} not found.")
            return

        agent_id = result[0]
        cursor.execute('''
            INSERT INTO TIMESTAMPS (agent_id, start_processing, start_publishing, start_consumption)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, start_processing, start_publishing, start_consumption))
        connection.commit()
        print("[+] INFO: Timestamp inserted successfully.")

    except sqlite3.DatabaseError as e:
        print(f"[!!] ERROR inserting timestamp into database: {e}")
    finally:
        cursor.close()
