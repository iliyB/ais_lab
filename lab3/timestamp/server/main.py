import json
import logging
import socket
import time

from des import DesKey

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)

key_byte = b"\xbd\x9b\xe3g\x95\xb4\x13o\xa0\xb5#\xa1-t\xf6\x04"
session_id = "111"


def main():
    logger.debug(f"Start server with session_id - {session_id}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 7005))
    sock.listen(True)

    key = DesKey(key_byte)

    while True:
        connect, address = sock.accept()
        logger.debug("New connection")
        request = connect.recv(1024)
        logger.debug(f"Request: {request}")

        request = json.loads(key.decrypt(request, padding=True))
        logger.debug(f"Decrypt request: {request}")

        try:
            if request["session_id"] != session_id:
                logger.debug("Wrong session_id")
                raise Exception("")
            if int(request["timestamp"]) + 5 < time.time():
                logger.debug("Wrong timestamp")
                raise Exception("")
        except Exception:
            logger.debug("Wrong request")
            connect.send(bytes(False))
        else:
            logger.debug("Success authentication")
            connect.send(bytes(True))


if __name__ == "__main__":
    main()
