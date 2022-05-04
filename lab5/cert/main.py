import logging
import sys
import socket
import json

sys.path.insert(0, "../../")
from lab5.utils import get_logger, generate

logger = get_logger(logging.getLogger(__name__))


def connection(n):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 6505))
    sock.listen(True)

    while True:
        connect, address = sock.accept()
        logger.debug("Был получен новый запрос")

        data = connect.recv(1024)
        json_data = json.loads(data.decode("utf-8"))
        logger.debug(f"Запрос: {json_data}")
        try:
            g_send = json_data["send"]
        except KeyError:
            logger.warning("Ошибка разбора json-oбъекта")
            continue

        result = {}
        result["send"] = g_send
        result["n"] = n
        logger.debug(f"Ответ собран {result}")
        connect.sendall(bytes(json.dumps(result), encoding="utf-8"))
        logger.debug("Ответ отправлен")
        logger.debug("-------------------------------------")


def main():
    n = generate()
    logger.debug(f"Ключ сессии {n}")
    connection(n)


if __name__ == "__main__":
    main()
