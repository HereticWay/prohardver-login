#!/usr/bin/env python3
import requests
import requests.utils
import re
import time
import os
import logging

ID_PATTERN = '(?<=name="fidentifier" value=")(.*)(?="\\/>)'
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

BOUNDARY = '----FCK-BOUNDARIES'
LOGIN_URL = 'https://prohardver.hu/muvelet/hozzaferes/belepes.php?url=%2Findex.html'
PROTECTED_PAGE_URL = 'https://prohardver.hu/tema/bestbuy_topik_akcio_ajanlasakor_akcio_hashtag_kote/friss.html'



def get_fidentifier(session: requests.Session) -> str:
    r = session.get(LOGIN_URL)

    match = re.search(ID_PATTERN, r.text)
    if not match:
        raise Exception('No match for fidentifier!')

    return match.group()


def login(session: requests.Session, fidentifier: str, email: str, password: str) -> None:
    request = requests.Request('POST', LOGIN_URL, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': f'multipart/form-data; boundary={BOUNDARY}',
        'Origin': 'https://prohardver.hu',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://prohardver.hu/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'TE': 'trailers'
    })
    requests.utils.add_dict_to_cookiejar(session.cookies, {
        'login-options': '{"stay":false,"no_ip_check":false,"leave_others":false}'
    })

    login_request = session.prepare_request(request)
    login_request.body = (
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="fidentifier"\r\n\r\n'
        f'{fidentifier}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="email"\r\n\r\n'
        f'{email}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="pass"\r\n\r\n'
        f'{password}\r\n'
        f'--{BOUNDARY}--\r\n'
    )
    login_request.prepare_content_length(login_request.body)

    print(f'Headers: {login_request.headers}')
    print(f'Body: {login_request.body}')

    response: requests.Response = session.send(login_request)
    print(response.content)
    print(response.headers)


def request_protected_page(session: requests.Session) -> str:
    response = session.get(PROTECTED_PAGE_URL)
    return response.text


def main() -> None:
    with requests.Session() as session:
        fidentifier = get_fidentifier(session)
        print(session.cookies)

        time.sleep(0.1)
        login(session, fidentifier, EMAIL, PASSWORD)

        time.sleep(0.1)
        page_str = request_protected_page(session)
        print(page_str)


if __name__ == '__main__':
    main()
