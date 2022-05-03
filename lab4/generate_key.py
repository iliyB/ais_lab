import logging

import rsa

from utils import get_logger

logger = get_logger(logging.getLogger(__name__))

nodes = ["A", "B", "D", "F"]

for node in nodes:
    logger.info(f"Генерация ключей rsa для {node}")


    (pk, sk) = rsa.newkeys(1024)

    pk_p = pk.save_pkcs1('PEM')
    sk_p = sk.save_pkcs1('PEM')
    with open(f"sk{node}", "wb") as file:
        file.write(sk_p)

    with open(f"pk{node}", "wb") as file:
        file.write(pk_p)

    logger.info(f"Ключи rsa для {node} сгенерированы")