import datetime
import json
import threading

import pika
from retry import retry


class RabbitMq:
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

    def on_received_message(self, blocking_channel, deliver, properties,
                            message):
        print("on_received_message()")
        result = json.loads(message.decode('utf-8'))  # Decodează și parsează mesajul JSON

        with open('received_data.txt', 'a') as file:
            file.write(
                f"Thread-ul consumer {threading.current_thread().name} LA ORA {datetime.datetime.now()} a  primit date: {json.dumps(result)}\n\n\n")

        # print("result = message.decode('utf-8') ", result)
        blocking_channel.confirm_delivery()
        try:
            print("AM PRIMIT MESAJUL: ")
        except Exception as e:
            print(e)
            print("wrong data format")
        finally:
            blocking_channel.stop_consuming()


    def receive_message(self):
        print("receive_message()")
        with pika.BlockingConnection(self.parameters) as connection:
            print(" with pika.BlockingConnection(self.parameters) as connection:")
            with connection.channel() as channel:
                print(" with connection.channel() as channel:")

                method_frame, header_frame, body = channel.basic_get(self.config['queue'])

                if body is not None:
                    self.on_received_message(channel, method_frame, None, body)
                    channel.basic_ack(method_frame.delivery_tag)
                else:
                    print("No message returned")

    def clear_queue(self, channel):
        channel.queue_purge(self.config['queue'])
