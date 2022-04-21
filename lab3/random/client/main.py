import json
import logging
import random
import socket
import string
import sys

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
    sock.connect(("localhost", 7030))
    logger.debug("Success connection")

    A = "".join(random.choice(string.ascii_lowercase) for i in range(4))
    request = {"A": A}
    logger.debug(f"Message: {request}")
    request = bytes(json.dumps(request), "utf-8")
    logger.debug("Send request")
    sock.send(request)

    response = sock.recv(1024)
    logger.debug("Get response")
    key = DesKey(key_byte)
    logger.debug(f"Encrypt response: {response}")
    response = json.loads(key.decrypt(response, padding=True))
    logger.debug(f"Decrypt response: {response}")

    try:
        if A != response["A"]:
            logger.debug("Wrong A")
            raise Exception("")
        if session_id != response["session_id"]:
            logger.debug("Wrong session_id")
            raise Exception("")
        B = response["B"]
    except Exception:
        logger.debug("Wrong response")
        sys.exit(1)

    request = {
        "A": A,
        "B": B
    }
    logger.debug(f"Request: {request}")
    request = bytes(json.dumps(request), "utf-8")
    request = key.encrypt(request, padding=True)
    logger.debug(f"Encrypt request: {request}")
    logger.debug("Send request")
    sock.send(request)


    response = sock.recv(1024)
    logger.debug(f"Get response {response}")
    response = bool(response.decode("utf-8"))
    logger.debug(f"Success authentication: {response}")


if __name__ == "__main__":
    connection()
