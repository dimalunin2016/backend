
import pika
import traceback, sys
import smtplib
import socket
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

gmail_user = 'loginov.ra@phystech.edu'
gmail_password = 'roman1998'

def send_email(body):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    body = str(body)
    send_to, url = body[2: -1].split(';')

    html = "<p>Welcome! Thanks for signing up. Please follow this link to activate your account:</p>\n" \
            "<p><a href=\"{}\">{}</a></p>\n" \
            "<br>\n" \
            "<p>Cheers!</p>".format(url, url)

    text = "Link for email confirmation: {}\n Follow it and join the amazing service!".format(url)

    text_letter = MIMEText(text, 'plain')
    letter = MIMEText(html, 'html')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Email confirmation'
    msg['From'] = gmail_user
    msg['To'] = send_to
    msg.attach(text_letter)
    msg.attach(letter)

    server.sendmail(gmail_user, [send_to], msg.as_string())
    print('Sent email to {}'.format(send_to))
    server.close()

def wait_for_port(addr, port, timeout=1):
    i = 0
    while True:
        i += 1
        print("Attempt #{} connecting to {}:{}".format(i, addr, port))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((addr, int(port)))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            print("Success!")
            return
        except OSError as err:
            print("Failure!")
            time.sleep(timeout)

wait_for_port("krolik", 5672)

conn_params = pika.ConnectionParameters('krolik', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

channel.queue_declare(queue='email-queue', durable = True)

print("Waiting for messages. To exit press CTRL+C")

def callback(ch, method, properties, body):
    send_email(body)

channel.basic_consume('email-queue', callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception as ex:
    print(type(ex).__name__)
    channel.stop_consuming()

traceback.print_exc(file=sys.stdout)
