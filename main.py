import logging
import os
import sys
import typing

import instagrapi
import dotenv

# Globals
logging.basicConfig()
log: logging.Logger = logging.getLogger()
DEFAULT_SESSION_FILEPATH: str = "session.json"


def get_session_filepath():
    res = os.getenv("SESSION_FILEPATH")
    if res is None:
        return DEFAULT_SESSION_FILEPATH
    else:
        return res


def login_user(client: instagrapi.Client):
    """
    Attempts to login to Instagram first with session data, then with credentials if failed
    """
    login_via_session = False
    login_via_pw = False

    SESSION_FILEPATH = get_session_filepath()
    log.info("Session filepath is %s", SESSION_FILEPATH)

    session = False
    if os.path.exists(SESSION_FILEPATH):
        session = client.load_settings(SESSION_FILEPATH)

    # Load from environment variables
    ACCOUNT_USERNAME = os.getenv("ACCOUNT_USERNAME")
    ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")

    if session:
        try:
            client.set_settings(session)
            client.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)

            # check if session is valid
            try:
                client.get_timeline_feed()
            except instagrapi.LoginRequired:
                log.info("Session is invalid, need to login via username and password")

                old_session = client.get_settings()

                # use the same device uuids across logins
                client.set_settings({})
                client.set_uuids(old_session["uuids"])

                client.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
            login_via_session = True
        except Exception as e:
            log.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            log.info("Attempting to login via username and password. username: %s" % ACCOUNT_USERNAME)
            if client.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD):
                login_via_pw = True
                client.dump_settings(SESSION_FILEPATH)
        except Exception as e:
            log.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")


def init() -> instagrapi.Client:
    """
    Initialize any pre-connection variables, loggers, etc. and returns a Client object
    :return: Client object
    """

    # Configure root logger settings here
    log.setLevel(logging.INFO)

    # Client logger setup
    client_logger = logging.getLogger("client")
    client_logger.setLevel(logging.INFO)

    log.info("Reading environment variables...")
    dotenv.load_dotenv()

    return instagrapi.Client(logger=client_logger)


def main():
    client = init()

    log.info("Attempting login...")
    login_user(client)

if __name__ == '__main__':
    main()
