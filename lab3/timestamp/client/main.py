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
session_id = "222"


def connection():
    logger.debug("Init connection")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 7005))
    logger.debug("Success connection")

    request = {"timestamp": time.time(), "session_id": session_id}
    logger.debug(f"Message: {request}")

    request = bytes(json.dumps(request), "utf-8")
    key = DesKey(key_byte)
    request = key.encrypt(request, padding=True)
    logger.debug(f"Encrypt message: {request}")

    logger.debug("Send request")
    sock.send(request)

    response = sock.recv(1024)
    logger.debug(f"Get response {response}")

    response = bool(response.decode("utf-8"))
    logger.debug(f"Success authentication: {response}")


if __name__ == "__main__":
    connection()
