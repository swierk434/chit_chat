import pika
import sys
from threading import Thread

def callback(ch, method, properties, body):
    print(f" Received: {body.decode()}")

def get_user_input(prompt="Enter message (type 'exit' to quit): "):
    return input(prompt)

def connect(hostname, username, password):
    connectionparams = pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('swierk', 'swierk2000'))
    connection = pika.BlockingConnection(connectionparams)
    channel = connection.channel()
    return channel, connection

def reciver(channel, connection):
    channel.exchange_declare(exchange='chat', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='chat', queue=queue_name)

    print(' Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

def sender(channel, connection):
    try:
        while True:
            message = get_user_input()
            if message == 'exit':
                break

            channel.basic_publish(exchange='chat', routing_key='', body=message)
            print(f" Sent: {message}")
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()

if __name__ == '__main__':
    channel, connection = connect('localhost', 'swierk', 'swierk2000')
    t1 = Thread(target=sender ,args=(channel, connection))
    t2 = Thread(target=reciver ,args=(channel, connection))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
