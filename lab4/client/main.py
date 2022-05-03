import logging
import socket
import sys

import rsa
import sqlite3
import json
import string
import random

sys.path.insert(0, "../../")
from lab4.utils import get_logger

logger = get_logger(logging.getLogger(__name__))
idB = "B"


def getR():
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(int(random.uniform(4, 6)))
    )


def db_connect():
    db = sqlite3.connect("lab3.sqlite")
    cursor = db.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cert"
        "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "ident TEXT NO NULL,"
        "sk TEXT NO NULL)"
    )

    db.commit()
    cursor.execute("SELECT * from cert")

    if not (cursor.fetchall()):
        cursor.execute(
            "INSERT INTO cert ('ident', 'sk')"
            "VALUES ('A', 'skA'),"
            "('D', 'skD'),"
            "('F', 'skF')"
        )
        logger.debug("Write data")
        db.commit()


def db_getPrivareKey(target):
    db = sqlite3.connect("lab3.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT sk FROM cert WHERE ident = ?", [target])
    try:
        target_sk = cursor.fetchone()
    except Exception:
        logger.debug(f"Запрошенного пользователя нет в БД: {target}")
        exit(0)

    return target_sk


def connection_with_pki(current_user):
    logger.debug("Соединение с PKI")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 6505))
    target = "B"
    result = {}
    result["sended"] = current_user
    result["target"] = target
    logger.debug(f"json-собран: {result}")
    sock.sendall(bytes(json.dumps(result), encoding="utf-8"))
    logger.debug("json-отправлен")

    data = sock.recv(2048)
    logger.debug(f"Ответ получен: {data}")
    json_data = json.loads(data.decode("utf-8"))
    logger.debug(f"Данные от PKI получены: {json_data}")
    try:
        g_target = json_data["target"]
        g_pk = json_data["pk"]
        if g_target != target:
            logger.debug("Получено неверное значение target от PKI")
            exit(0)
    except KeyError:
        logger.debug("Ошибка разбора json-объекта")
        exit(0)
    logger.debug("--------------------------------")
    return g_pk


def connection_with_server(current_user, g_pk):
    logger.debug("Соединение с сервером")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 6500))
    target = "B"
    R_user = getR()

    # Первый шаг, отправка на сервер первого запроса
    logger.info("Первый шаг, отправка на сервер первого запроса")
    result = {}
    result["R_user"] = R_user
    result["ident_client"] = current_user
    logger.debug(f"json-собран: {result}")
    pubkey = rsa.PublicKey.load_pkcs1(g_pk)
    json_ = json.dumps(result)
    json_ = rsa.encrypt(json_.encode(), pubkey)
    sock.send(json_)
    logger.debug("Был отправлен запрос на сервер")
    logger.debug("--------------------------------")

    # Второй шаг, получение от сервера ответа
    logger.info("Второй шаг, получение от сервера ответа")
    secretkey = db_getPrivareKey(current_user)
    file = open(secretkey[0])
    secretkey = rsa.PrivateKey.load_pkcs1(file.read())
    data = sock.recv(2048)
    json_data = json.loads(rsa.decrypt(data, secretkey).decode())
    logger.debug(f"Получено ответ: {json_data}")
    try:
        R_client = json_data["R_user"]
        R_server = json_data["R_server"]
        g_server = json_data["ident"]
        logger.debug("Ответ от сервера расшифрован")
        if target != g_server:
            logger.debug("Получен ответ не от того сервера")
            exit(0)
        elif R_client != R_user:
            logger.debug("Получено другое случайное число")
            exit(0)
    except KeyError:
        logger.debug("Ошибка разбора json-объекта")
        exit(0)
    logger.debug("--------------------------------")

    # Третий шаг, отправка серверу Rb
    logger.info("Третий шаг, отправка серверу Rb")
    result = {}
    result["R_server"] = R_server
    logger.debug(f"json-собран: {result}")
    json_ = json.dumps(result)
    json_ = rsa.encrypt(json_.encode(), pubkey)
    sock.send(json_)
    logger.debug("Случайная строка сервера отправлена серверу")
    logger.debug("--------------------------------")

    # Пятый шаг, получение решения об аутентификации от сервера
    logger.info("Пятый шаг, получение решения об аутентификации от сервера")
    data = sock.recv(2048)
    json_data = json.loads(rsa.decrypt(data, secretkey).decode())
    try:
        end = json_data["end"]
        if end == 1:
            logger.debug("Аутентификация прошла успешно")
            input()
        else:
            logger.debug("Аутентификация не удалась")
            exit(0)
    except KeyError:
        logger.debug("Ошибка разбора json-объекта")
        exit(0)


def main():
    db_connect()
    logger.debug(
        "Выберите пользователя, под котором необходимо совершить сеанс аутентификации"
    )
    logger.debug("Доступные варианты: A, D, F")
    user = input()
    while (user != "A") and (user != "D") and (user != "F"):
        logger.debug("Введен неправильный пользователь, повторите попытку")
        user = input()
    current_user = user
    pk = connection_with_pki(current_user)
    connection_with_server(current_user, pk)


if __name__ == "__main__":
    main()
