import logging
import socket
import json
import sqlite3
import sys

sys.path.insert(0, "../../")
from lab4.utils import get_logger

logger = get_logger(logging.getLogger(__name__))


def db_connect():
    db = sqlite3.connect("lab3.sqlite")
    cursor = db.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cert"
        "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "ident TEXT NO NULL,"
        "pk TEXT NO NULL)"
    )

    db.commit()
    cursor.execute("SELECT * from cert")

    if not (cursor.fetchall()):
        cursor.execute(
            "INSERT INTO cert ('ident', 'pk')"
            "VALUES ('A', 'pkA'),"
            "('D', 'pkD'),"
            "('F', 'pkF'),"
            "('B', 'pkB')"
        )
        logger.debug("Write data")
        db.commit()


def db_getPublickKey(target):
    db = sqlite3.connect("lab3.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT pk FROM cert WHERE ident = ?", [target])
    try:
        target_pk = cursor.fetchone()
    except Exception:
        logger.debug("Запрошенного пользователя нет в БД: " + target)

    return target_pk


def connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 6505))
    sock.listen(True)

    while True:
        connect, address = sock.accept()
        logger.debug("Был подключено новое соединение")
        data = connect.recv(2048)
        json_data = json.loads(data.decode("utf-8"))
        logger.debug(f"Получен json: {json_data}")
        try:
            g_target = json_data["target"]
            logger.debug("json-разобран")
        except KeyError:
            logger.debug("Ошибка разбора json-объекта")
            continue

        target_pk = db_getPublickKey(g_target)
        result = {}
        result["target"] = g_target
        file = open(target_pk[0])
        result["pk"] = file.read()

        json_ = json.dumps(result)
        connect.sendall(bytes(json_, encoding="utf-8"))

        logger.debug("Ответ отправлен")
        logger.debug("--------------------------------")


def main():
    db_connect()
    connection()


if __name__ == "__main__":
    main()
