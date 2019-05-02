import json
import pika
import os
import time
import requests
from rabbit_connector import AMQPServer

# TODO: smart_home_server_address should be stored in data base
smart_home_server_address = 'http://smarthome.8wkc8cx8wzmkblhw.myfritz.net/devices'
default = 'http://localhost:5672'
url = os.environ.get('CLOUDAMQP_URL', default)
print(url)
params = pika.URLParameters(url)


def setup_listener():
    global server
    server.channel.exchange_declare(exchange='sh_exchange', exchange_type='topic', durable=True)
    server.channel.queue_declare(queue='sh_device')
    server.channel.queue_declare(queue='sh_device_list')
    server.channel.queue_bind(queue='sh_device', exchange='sh_exchange', routing_key='device.*')
    server.channel.queue_bind(queue='sh_device_list', exchange='sh_exchange', routing_key='device_list.*')

    @server.register('sh_device_list', sync=True)
    def device_list(res):
        routing_key = res['routing_key']
        command = routing_key.split('.')
        command = command[1]

        if command is not 'get':
            payload = res['body']
            payload = json.loads(payload)

        if command is 'get':
            return requests.get(smart_home_server_address)

        elif command is 'add':
            if not all(parameter in payload for parameter in ['device_id', 'device_name', 'device_type',
                                                              'device_controller_address', 'device_data']):
                return 'Invalid payload, one or more parameters are missing'
            else:
                return requests.post('/devices', json=payload)

        else:
            status = {'status': 'Error: Unknown command: {}'.format(command)}
            return json.dumps(status)

    @server.register('sh_device', sync=True)
    def device(res):
        routing_key = res['routing_key']
        command = routing_key.split('.')
        command = command[1]
        payload = res['body']
        payload = json.loads(payload)
        device_id = payload['device_id']
        device_path = '{}/{}'.format(smart_home_server_address, device_id)

        if command is 'get':
            return requests.get(device_path)

        elif command is 'set':
            return requests.patch(device_path, json=payload)

        elif command is 'delete':
            return requests.delete(device_path)

        else:
            status = {'status': 'Error: Unknown command: {}'.format(command)}
            return json.dumps(status)


if __name__ == '__main__':
    global server
    connection = pika.BlockingConnection(params)
    server = AMQPServer(connection)

    setup_listener()

    server.start_listening()

    while True:
        time.sleep(5)

    server.disconnect()
