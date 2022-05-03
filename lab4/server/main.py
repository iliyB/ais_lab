import logging
import socket
import sys

import rsa
import json
import string
import random

sys.path.insert(0, "../../")
from lab4.utils import get_logger

logger = get_logger(logging.getLogger(__name__))
idB = "B"
skB = "skB"


def getR():
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(int(random.uniform(4, 6)))
    )


def connection_with_pki(target):
    logger.debug("Соединение с PKI")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 6505))
    current_user = "B"
    result = {}
    result["sended"] = current_user
    result["target"] = target
    logger.debug(f"json-собран: {result}")
    sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
    logger.debug("json-отправлен")

    data = sock.recv(2048)
    logger.debug("Ответ получен")
    json_data = json.loads(data.decode("utf-8"))
    logger.debug(f"Полученный json: {json}")
    try:
        g_target = json_data["target"]
        g_pk = json_data["pk"]
        if g_target != target:
            logger.debug("Получено неверное значение target от PKI")
            exit(0)
    except KeyError:
        logger.debug("Ошибка разбора json-объекта")
    logger.debug("--------------------------------")
    return g_pk


def connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 6500))
    sock.listen(True)

    while True:
        connect, addres = sock.accept()
        logger.debug("Был подключено новое соединение")

        file = open(skB)
        secretkey = rsa.PrivateKey.load_pkcs1(file.read())

        # Первый шаг, получение первого сообщения от сервера
        logger.info("Первый шаг, получение первого сообщения от сервера")
        data = connect.recv(2048)
        json_data = json.loads(rsa.decrypt(data, secretkey).decode())
        try:
            R_client = json_data["R_user"]
            g_client = json_data["ident_client"]
            logger.debug(f"Запрос расшифрован, запрос поступил от {g_client}")
        except KeyError:
            logger.debug("Ошибка разбора json-объекта")
            continue
        logger.debug("--------------------------------")

        # Второй шаг, отправка запроса PKI
        logger.info("Второй шаг, отправка запроса PKI")
        pk = connection_with_pki(g_client)

        # Третий шаг, отправка ответа клиенту
        logger.info("Третий шаг, отправка ответа клиенту")
        rb = getR()
        result = {}
        result["R_user"] = R_client
        result["R_server"] = rb
        result["ident"] = idB
        logger.debug(f"json-собран {json}")
        pubkey = rsa.PublicKey.load_pkcs1(pk)
        json_ = json.dumps(result)
        json_ = rsa.encrypt(json_.encode(), pubkey)
        connect.send(json_)
        logger.debug("Ответ отправлен клиенту")
        logger.debug("--------------------------------")

        # Четвертый шаг, получение ответа от клиента
        logger.info("Четвертый шаг, получение ответа от клиента")
        data = connect.recv(2048)
        json_data = json.loads(rsa.decrypt(data, secretkey).decode())
        try:
            R_server = json_data["R_server"]
            if rb != R_server:
                logger.debug("Было получено неверное число от клиента " + g_client)
                continue
            else:
                logger.debug("Было получено правильное число от клиента " + g_client)
        except KeyError:
            logger.debug("Ошибка разбора json-объекта")
            continue

        logger.debug("--------------------------------")

        # Пятый шаг, отправка клиенту информации об аутентификации
        logger.info("Пятый шаг, отправка клиенту информации об аутентификации")
        result = {}
        result["end"] = 1
        logger.debug("json-собран")
        pubkey = rsa.PublicKey.load_pkcs1(pk)
        json_ = json.dumps(result)
        json_ = rsa.encrypt(json_.encode(), pubkey)
        connect.send(json_)
        logger.debug("Клиента отправлено сообщение об успешной аутентификации")
        logger.debug("--------------------------------")


def main():
    connection()


if __name__ == "__main__":
    main()
