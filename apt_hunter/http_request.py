from bs4 import BeautifulSoup
import requests
import time
import logging


HTTP_SLEEP_DELAY = 1  # seconds
HTTP_TIMEOUT = 5  # seconds
HTTP_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"


def html_request(url):
    try:
        request_header = {'user-agent': HTTP_USER_AGENT}
        url_response = requests.get(url, headers=request_header, timeout=HTTP_TIMEOUT)
        time.sleep(HTTP_SLEEP_DELAY)
    except requests.exceptions.Timeout:
        logging.error(f'HTTP TIMEOUT. URL: {url}')
        return None
    return BeautifulSoup(url_response.content, "html.parser")


def json_request(url):
    try:
        url_response = requests.get(url, timeout=HTTP_TIMEOUT)
    except requests.exceptions.Timeout:
        logging.error(f'HTTP TIMEOUT. URL: {url}')
        return None
    return url_response.json()
