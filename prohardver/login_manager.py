import requests
import requests.utils
import re
import time
import logging
from . import exceptions


FORM_ID_PATTERN = '(?<=name="fidentifier" value=")(.*)(?="\\/>)'
LOGIN_URL = 'https://prohardver.hu/muvelet/hozzaferes/belepes.php?url=%2Findex.html'
BOUNDARY = '----FCK-BOUNDARIES'
_HTTP_REQUEST_TIMEOUT = 5000


class LoginManager:
    __session: requests.Session = None

    def __init__(self, session: requests.Session) -> None:
        self.__session = session

    def __get_form_identifier(self) -> str:
        """Extract form identifier from the login page"""
        response = self.__session.get(LOGIN_URL, timeout=_HTTP_REQUEST_TIMEOUT)
        response.raise_for_status()

        match = re.search(FORM_ID_PATTERN, response.text)
        if not match:
            raise exceptions.WebScrapeFailureException('No match for form identifier "fidentifier"!')

        return match.group()

    def login(self, email: str, password: str) -> None:
        """Make the necessary steps to log in to the webpage with the given credentials in the current session"""
        form_identifier = self.__get_form_identifier()
        time.sleep(0.1)  # We don't want to DOS the server with our requests

        # Build a custom request with normal browser-like headers
        request = requests.Request('POST', LOGIN_URL, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': f'multipart/form-data; boundary={BOUNDARY}',  # Must use multipart/form-data type here
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

        requests.utils.add_dict_to_cookiejar(self.__session.cookies, {
            'login-options': '{"stay":false,"no_ip_check":false,"leave_others":false}'
        })

        login_request = self.__session.prepare_request(request)
        # Make a custom body for multipart/form-data content type because requests doesn't support this by default and
        # prohardver.hu uses this for some reason instead of the regular application/x-www-form-urlencoded format.
        login_request.body = (
            f'--{BOUNDARY}\r\n'
            f'Content-Disposition: form-data; name="fidentifier"\r\n\r\n'
            f'{form_identifier}\r\n'
            f'--{BOUNDARY}\r\n'
            f'Content-Disposition: form-data; name="email"\r\n\r\n'
            f'{email}\r\n'
            f'--{BOUNDARY}\r\n'
            f'Content-Disposition: form-data; name="pass"\r\n\r\n'
            f'{password}\r\n'
            f'--{BOUNDARY}--\r\n'
        )
        login_request.prepare_content_length(login_request.body)

        logging.info('This exact data will be sent to the server:')
        logging.info(f'Headers: {login_request.headers}')
        logging.info(f'Body: {login_request.body}')

        # Send the actual login request
        response: requests.Response = self.__session.send(login_request)
        logging.info('Response got back from the server:')
        logging.info(f'Headers: {response.headers}')
        logging.info(f'Content: {response.content}')
