import psutil
import requests
import socket
import time

SERVER_URL = 'http://16.16.253.13:5000/data'

INTERVAL = 3

def get_system_info():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage

def send_data(cpu_usage, ram_usage):
    data = {
        'machine_id': socket.gethostname(),  # Идентификатор машины, например, имя хоста
        'cpu_usage': cpu_usage,
        'ram_usage': ram_usage
    }
    try:
        response = requests.post(SERVER_URL, json=data)
        print(f'Data sent: {data} - Status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send data: {e}')

if __name__ == '__main__':
    while True:
        cpu_usage, ram_usage = get_system_info()
        send_data(cpu_usage, ram_usage)
        time.sleep(INTERVAL)

