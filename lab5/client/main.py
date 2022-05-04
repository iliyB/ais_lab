import logging
import sys
import json
import socket
import random

sys.path.insert(0, "../../")
from lab5.utils import get_logger

logger = get_logger(logging.getLogger(__name__))



def connection_with_T():
    logger.debug("Соединение с T")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 6505))

    result = {}
    result["send"] = "A"
    logger.debug(f"Тело запроса {result}")
    sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
    logger.debug("Запрос отправлен")

    data = sock.recv(1024)
    logger.debug("Ответ на запрос получен")
    json_data = json.loads(data.decode("utf-8"))
    logger.debug(f"Тело запроса {json_data}")
    try:
        g_send = json_data["send"]
        n = json_data["n"]
        logger.debug("Ответ разобран")
        if g_send != "A":
            logger.warning("Неправильное значение поля send")
            exit(0)
    except KeyError:
        logger.warning("Ошибка разбора json-oбъекта")
        exit(0)
    logger.debug("-------------------------------------")
    return n


def connection(n, b, a):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 6500))
    logger.debug("Подключение к серверу")

    for i in range(3):
        r = random.randint(1, n - 1)
        request = (r * r) % n
        result = {}
        result["r"] = r
        result["request"] = request
        if i == 0:
            result["send"] = "A"
            result["b"] = b
        logger.debug(f"Итерация {i + 1}, r = {r} request =  {request}")

        sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
        logger.debug("Данные отправлены")

        data = sock.recv(1024)
        json_data = json.loads(data.decode("utf-8"))
        logger.debug("Получен ответ от сервера")

        try:
            x = json_data["x"]
            logger.debug(f"Значение x - {x}")
        except KeyError:
            logger.warning("Ошибка разбора json-объекта")
            exit(0)

        if x == 0:
            response = r
        else:
            response = (r * a) % n
        logger.debug(f"Значение response = {response} отправлено серверу")
        result = {}
        result["response"] = response
        sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
        logger.debug("-------------------------------------")
        if i == 2:
            logger.debug("Аутентификация пройдена успешно")


def main():
    n = connection_with_T()
    a = random.randint(1, n - 1)
    b = (a * a) % n
    logger.debug(f"Значение a - {a}")
    logger.debug(f"Значение b - {b}")
    logger.debug("-------------------------------------")
    connection(n, b, a)


if __name__ == "__main__":
    main()
