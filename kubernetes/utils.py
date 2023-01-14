import socket
import random
import uuid
import datetime
from requests import get

HOST: str = get("https://ipinfo.io/ip").text


def get_name() -> str:
    return "".join(
        [
            random.choice("bcdfghjklmnpqrstvwxyz") + random.choice("aeiou")
            for i in range(random.randint(3, 5))
        ]
    ).capitalize()


def get_password() -> str:
    return "".join(
        [
            random.choice("bcdfghjklmnpqrstvwxyz0123456789")
            for i in range(random.randint(8, 12))
        ]
    )


def get_id() -> str:
    return str(uuid.uuid4())


def get_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_port() -> int:
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind(("", 0))
    port = socket_server.getsockname()[1]
    socket_server.close()
    return port


def get_host() -> str:
    return HOST
