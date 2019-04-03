
import pika
import traceback, sys

conn_params = pika.ConnectionParameters('localhost', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

channel.queue_declare(queue='email-queue', durable = True)

print("Waiting for messages. To exit press CTRL+C")

def callback(ch, method, properties, body):
    print(body)

channel.basic_consume(callback, queue='email-queue')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()

traceback.print_exc(file=sys.stdout)
