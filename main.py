#!/usr/bin/env python3
import requests
import requests.utils
import os
import logging
import prohardver

PROTECTED_PAGE_URL = 'https://prohardver.hu/tema/bestbuy_topik_akcio_ajanlasakor_akcio_hashtag_kote/friss.html'
HTTP_REQUEST_TIMEOUT = 5000


def request_protected_page(session: requests.Session) -> str:
    response = session.get(PROTECTED_PAGE_URL, timeout=HTTP_REQUEST_TIMEOUT)
    response.raise_for_status()  # Raise exception if any HTTPError occurs

    return response.text


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    with requests.Session() as session:
        login_manager = prohardver.LoginManager(session)
        login_manager.login(email, password)

        page_str = request_protected_page(session)
        logging.info(f'Protected webpage:')
        logging.info(page_str)


if __name__ == '__main__':
    main()
