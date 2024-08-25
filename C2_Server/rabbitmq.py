"""
 File: rabbitmq.py
 Description: file for implement communication with Rabbitmq queue - consume alerts published by Log Collector
 Designed by: Pasa Larisa

 Module-History:
    3. Save elements in local queue + ack for delivery
    2. Modify receive feature to consume just 1 element from queue ( each thread process 1 element from queue)
    1. Add configuration for queue
"""
import datetime
import inspect
import json
import logging
import threading
from constants import *
import pika


class RabbitMq:
    """
      RabbitMq is responsible for handling the connection and communication with a RabbitMQ server.

      Attributes:
      config (dict): Configuration details for connecting to RabbitMQ.
      credentials (pika.PlainCredentials): Credentials for authenticating with RabbitMQ.
      parameters (pika.ConnectionParameters): Parameters for connecting to RabbitMQ.
    """
    config = {
        'host': '0.0.0.0',
        'port': 5672,
        'username': 'student',
        'password': 'student',
        'exchange': 'tpeexample.direct',
        'routing_key': 'tpeexample.routingkey',
        'queue': 'tpeexample.queue'
    }
    credentials = pika.PlainCredentials(config['username'], config['password'])
    parameters = (pika.ConnectionParameters(host=config['host']),
                  pika.ConnectionParameters(port=config['port']),
                  pika.ConnectionParameters(credentials=credentials))


    def on_received_message(self, blocking_channel, deliver, properties, message):
        """
             Callback function that is invoked when a message is received from the RabbitMQ queue.

             Parameters:
             blocking_channel (pika.adapters.blocking_connection.BlockingChannel): The channel object the message was received on.
             deliver (pika.spec.Basic.Deliver): Delivery properties of the message.
             properties (pika.spec.BasicProperties): Message properties.
             message (bytes): The message body received from the queue.

             Returns:
             None
         """

        try:
            result = json.loads(message.decode('utf-8'))

            # Add timestamp for moment of consuming from queue
            add_publishing_timestamp = lambda alert: {**alert, TIMESTAMP_SUBDOCUMENT: {**alert[TIMESTAMP_SUBDOCUMENT], CONSUMPTION_FIELD: str(datetime.datetime.now())}}
            formatted_alerts = list(map(add_publishing_timestamp, result))

            ALERTS_QUEUE.put(formatted_alerts)
            blocking_channel.confirm_delivery()

        except json.JSONDecodeError as e:
            logging.error(f"[!!][on_received_message] ERROR: decode JSON: {e}")
            print(f"[!!][on_received_message] ERROR: decode JSON: {e}")

        except ALERTS_QUEUE.Full as e:
            logging.error(f"[!!][on_received_message] ERROR: Queue is full: {e}")
            print(f"[!!][on_received_message] ERROR: Queue is full: {e}")

        except Exception as e:
            logging.error(f"[!!][on_received_message] ERROR: {e}")
            print(f"[!!][on_received_message] ERROR: {e}")
        finally:
            blocking_channel.stop_consuming()

    def receive_message(self):
        """
            Function which create new connection + channel for each thread to publish alerts in queue

            Returns:
            None
        """
        with pika.BlockingConnection(self.parameters) as connection:
            with connection.channel() as channel:
                method_frame, header_frame, body = channel.basic_get(self.config['queue'])
                if body is not None:
                    self.on_received_message(channel, method_frame, None, body)
                    channel.basic_ack(method_frame.delivery_tag)
                else:
                    pass

    def clear_queue(self, channel):
        channel.queue_purge(self.config['queue'])
