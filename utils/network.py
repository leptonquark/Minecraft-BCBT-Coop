START_PORT = 10000
IP = "127.0.0.1"


def get_ports(n):
    return [START_PORT + i for i in range(n)]


def get_ip():
    return IP
