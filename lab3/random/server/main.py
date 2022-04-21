import json
import logging
import random
import socket
import string

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
    sock.bind(("localhost", 7030))
    sock.listen(True)

    key = DesKey(key_byte)

    while True:
        connect, address = sock.accept()
        logger.debug("New connection")
        request = connect.recv(1024)
        logger.debug(f"Request: {request}")

        request = json.loads(bytes.decode(request, "utf-8"))

        try:
            A = request["A"]
        except Exception:
            logger.debug("Wrong request")
            continue

        B = "".join(random.choice(string.ascii_lowercase) for i in range(4))
        response = {
            "A": A,
            "B": B,
            "session_id": session_id
        }
        logger.debug(f"Response: {response}")
        response = bytes(json.dumps(response), "utf-8")
        response = key.encrypt(response, padding=True)
        logger.debug(f"Encrypt response: {response}")
        logger.debug("Response send")
        connect.send(response)

        request = connect.recv(1024)
        logger.debug(f"Get request: {request}")
        try:
            request = json.loads(key.decrypt(request, padding=True))
        except Exception:
            logger.debug(f"Invalid connection")
            continue

        logger.debug(f"Decrypt request: {request}")

        try:
            if A != request["A"]:
                logger.debug("Wrong A")
                raise Exception("")
            if B != request["B"]:
                logger.debug("Wrong B")
                raise Exception("")
        except Exception:
            logger.debug("Wrong response")
            connect.send(bytes(0))
        else:
            logger.debug("Success authentication")
            connect.send(bytes(True))


if __name__ == "__main__":
    main()
