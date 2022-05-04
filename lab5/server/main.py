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
    result["send"] = "B"
    logger.debug(f"Тело запроса {result}")
    sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
    logger.debug("Запрос отправлен")

    data = sock.recv(1024)
    logger.debug("Ответ на запрос получен")
    json_data = json.loads(data.decode("utf-8"))
    logger.debug(f"Ответ {json_data}")
    try:
        g_send = json_data["send"]
        n = json_data["n"]
        logger.debug("Ответ разобран")
        if g_send != "B":
            logger.warning("Неправильное значение поля send")
            exit(0)
    except KeyError:
        logger.warning("Ошибка разбора json-oбъекта")
        exit(0)
    logger.debug("-------------------------------------")
    return n


def connection(n):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 6500))
    sock.listen(True)

    while True:
        connect, addres = sock.accept()
        logger.debug("Установлено новое соединение")
        b = 0

        for i in range(3):
            data = connect.recv(1024)
            json_data = json.loads(data.decode("utf-8"))
            logger.debug(f"Получено сообщение {json_data}")
            try:
                if i == 0:
                    g_send = json_data["send"]
                    b = json_data["b"]
                    logger.debug(f"Попытка аутентификации от клиента {g_send}")
                    logger.debug(f"Открытый ключ клиента - {b}")
                    logger.debug("-------------------------------------")
                request = json_data["request"]
                r = json_data["r"]
                logger.debug("Итерация {i + 1}, r = {r} request = {request}")
            except KeyError:
                logger.debug("Ошибка разбора json-объекта")
                break

            x = random.randint(0, 1)

            result = {}
            result["x"] = x
            connect.sendall(bytes(json.dumps(result), encoding="utf-8"))
            logger.debug("Число x = {x} отправлено")

            data = connect.recv(1024)
            json_data = json.loads(data.decode("utf-8"))
            logger.debug(f"Ответ получен {json_data}")
            try:
                response = json_data["response"]
                logger.debug(f"Значение response = {response} получено")
            except KeyError:
                logger.warning("Ошибка разбора json-объекта")
                break

            if x == 0:
                y1 = request % n
                y2 = (response * response) % n
                if y1 != y2:
                    logger.warning("Соединение с клиентам разорвано, числа не сходятся")
                    break
            else:
                y1 = (request * b) % n
                y2 = (response * response) % n
                if y1 != y2:
                    logger.warning("Соединение с клиентам разорвано, числа не сходятся")
                    break
            if i == 2:
                logger.debug("Клиент прошел атунетификацию")
            logger.debug("-------------------------------------")


def main():
    n = connection_with_T()
    logger.debug(f"N сеанса - {n}")
    logger.debug("-------------------------------------")
    connection(n)


if __name__ == "__main__":
    main()
