from bs4 import BeautifulSoup
import requests
import time
import logging

import SETTINGS


def html_request(url):
    try:
        request_header = {'user-agent': SETTINGS.USER_AGENT}
        url_response = requests.get(url, headers=request_header, timeout=SETTINGS.TIMEOUT)
        time.sleep(SETTINGS.SLEEP_DELAY)
    except requests.exceptions.Timeout:
        logging.error(f'HTTP TIMEOUT. URL: {url}')
        return None
    return BeautifulSoup(url_response.content, "html.parser")


def json_request(url):
    try:
        url_response = requests.get(url, timeout=SETTINGS.TIMEOUT)
    except requests.exceptions.Timeout:
        logging.error(f'HTTP TIMEOUT. URL: {url}')
        return None
    return url_response.json()
