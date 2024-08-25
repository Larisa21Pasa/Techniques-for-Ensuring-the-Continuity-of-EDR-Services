"""
 File: rabbitmq.py
 Description: file for implement communication with Rabbitmq queue - consume alerts published by Log Collector
 Designed by: Pasa Larisa

 Module-History:
    3. Add function to publish data
    1. Add configuration for queue
"""
import datetime
import inspect
import json
import logging
from util.constants import *
import pika
from retry import retry

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



    def send_message(self, formatted_alerts):
        """
           Fonction which publish alerts in RabbitMq queue

           Parameters:
           message : List with alerts from specific agent

           Returns:
           None
        """
        try:
            if not all(self.parameters):
                logging.error(f"[!!][send_message(self, formatted_alerts)] ERROR Parameters of connection are missing or are invalid")
                print(f"[!!][send_message(self, formatted_alerts)] ERROR Parameters of connection are missing or are invalid")
                return

            with pika.BlockingConnection(self.parameters) as connection:
                with connection.channel() as channel:
                    if not channel.is_open or not channel.queue_declare(queue=self.config['queue'], passive=True):
                        logging.error(f"[!!][send_message(self, formatted_alerts)] ERROR Channel or queue {self.config['queue']} does not exists")
                        print(f"[!!][send_message(self, formatted_alerts)] ERROR Channel or queue {self.config['queue']} does not exists")
                        return

                    add_publishing_timestamp = lambda alert: {**alert, TIMESTAMP_SUBDOCUMENT: {**alert[TIMESTAMP_SUBDOCUMENT], PUBLISHING_FIELD: str(datetime.datetime.now())}}
                    formatted_alerts = list(map(add_publishing_timestamp, formatted_alerts))
                    formatted_alerts = json.dumps(formatted_alerts, indent=4)
                    logging.info(f"[++][send_message(formatted_alerts)] INFO: Successfully processed alerts: \n************************************************************************\n{formatted_alerts}\n************************************************************************\n")
                    print(f"[++][send_message(formatted_alerts)] INFO: Successfully processed alerts: \n************************************************************************\n{formatted_alerts}\n************************************************************************\n")

                    formatted_alerts = formatted_alerts.encode()
                    channel.basic_publish(exchange=self.config['exchange'],
                                          routing_key=self.config['routing_key'],
                                          body=formatted_alerts)


        except pika.exceptions.AMQPError as e:
            logging.error(f"[!!][send_message(self, formatted_alerts)] ERROR AMQP: {e}")
            print(f"[!!][send_message(self, formatted_alerts)] ERROR AMQP: {e}")

        except Exception as e:
            logging.error(f"[!!][send_message(self, formatted_alerts)] ERROR Sending the message: {e}")
            print(f"[!!][send_message(self, formatted_alerts)] ERROR Sending the message: {e}")

    def clear_queue(self, channel):
        channel.queue_purge(self.config['queue'])
