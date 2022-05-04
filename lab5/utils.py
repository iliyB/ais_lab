import logging
import random
from logging import Logger
from math import sqrt


def get_logger(logger: Logger) -> Logger:
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def generate():
    p = 1
    q = 1
    lst = []
    for i in range(2, 50000000):
        if i > 10:
            if (i % 2 == 0) or (i % 10 == 5):
                continue
        for j in lst:
            if j > int((sqrt(i)) + 1):
                lst.append(i)
                if i > 5000:
                    if random.randint(1, 3000) == 3:
                        if p == 1:
                            p = i
                        elif q == 1:
                            q = i
                break
            if i % j == 0:
                break
        else:
            lst.append(i)
            if i > 5000:
                if random.randint(1, 3000) == 3:
                    if p == 1:
                        p = i
                    elif q == 1:
                        q = i
                        break
        if q != 1:
            break
    return p * q
