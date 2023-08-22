import getopt
import logging
import os
import sys
import typing

import instagrapi
import instagrapi.types
import dotenv

from login import login_user

# Globals
log: logging.Logger = logging.getLogger("main")


def get_inbox_threads(client: instagrapi.Client) -> typing.List[instagrapi.types.DirectThread]:
    return client.direct_threads(1)


def init() -> instagrapi.Client:
    """
    Initialize any pre-connection variables, loggers, etc. and returns a Client object
    :return: Client object
    """

    # Configure root logger settings here
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler())
    root_logger.setLevel(logging.INFO)
    # We're not setting the other logging levels, relying on propagation to root logger

    # Client logger setup
    client_logger = logging.getLogger("client")

    log.info("Reading environment variables...")
    dotenv.load_dotenv()

    return instagrapi.Client(logger=client_logger)


def main():
    client = init()

    log.info("Attempting login...")
    login_user(client)

    log.info("Retrieving inbox threads...")
    threads = get_inbox_threads(client)
    for thread in threads:
        print(thread)


if __name__ == '__main__':
    main()
