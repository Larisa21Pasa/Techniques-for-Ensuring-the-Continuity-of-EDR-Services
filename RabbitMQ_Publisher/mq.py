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

    def send_message(self, message):
        try:
            print("Trimit mesaj")

            if not all(self.parameters):
                print("Parametrii conexiunii lipsesc sau sunt invalizi.")
                return

            with pika.BlockingConnection(self.parameters) as connection:

                with connection.channel() as channel:
                    if not channel.is_open or not channel.queue_declare(queue=self.config['queue'], passive=True):
                        print(f"Canalul sau coada {self.config['queue']} nu există.")
                        return

                    # self.clear_queue(channel)
                    channel.basic_publish(exchange=self.config['exchange'],
                                          routing_key=self.config['routing_key'],
                                          body=message)

                    print("Mesajul a fost trimis cu succes.")

        except pika.exceptions.AMQPError as e:
            print(f"Eroare AMQP: {e}")
        except Exception as e:
            print(f"Eroare la trimiterea mesajului: {e}")

    def clear_queue(self, channel):
        channel.queue_purge(self.config['queue'])
