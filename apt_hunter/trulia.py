import logging
import datetime as dt
import re
import json

import http_request
import dbio


def get_search_entry(property_blob, property_url):
    page_jsons = property_blob.findAll('script', {'type': 'application/ld+json'})
    property_json = json.loads(page_jsons[2].text)['address']
    title = property_blob.find('title').text
    street_address = property_json['streetAddress']
    city = property_json['addressLocality']
    state = property_json['addressRegion']
    address = re.sub(r'([^0-9A-Za-z ,])+', '', ' '.join([street_address, city, state])).lower()
    re_match = r'([^0-9A-Za-z,#]+|[ ]{2,})'
    descript = re.sub(re_match, ' ', property_blob.find('p', {'id': 'propertyDescription'}).text)
    price_json = json.loads(page_jsons[1].text)['offers']
    price = price_json['price'] if 'price' in price_json else price_json['highPrice']
    return dbio.ApartmentEntry(address, price, property_url, title, descript)


def exceeds_max_age(date_blob, max_age):
    updated_match = re.match(r'Update: (\d\d/\d\d/\d\d\d\d \d\d:\d\d)[AP]M', date_blob.text)
    updated_dt = dt.datetime.strptime(updated_match.group(1), '%m/%d/%Y %H:%M')
    logging.info(f'Converted time: {updated_dt.strftime("%Y-%m-%d::%H:%M")}')
    return updated_dt < max_age


def get_script_json(html_blob):
    json_match = re.compile(r'var appState = (\{.+\});')
    for script in html_blob.find_all('script'):
        appState_json = json_match.search(script.text)
        if appState_json:
            return json.loads(appState_json.group(1))
    logging.error('Unable to locate script containing appState variable')
    return None


def search_page(html_blob, max_age, entry_list):
    current_time = dt.datetime.now()
    logging.info(f'Current time: {current_time.strftime("%Y-%m-%d::%H:%M")}')
    property_json = get_script_json(html_blob)
    if property_json is None:
        logging.error('Unable to locate property json. Page access probably denied')
        return False
    for property_card in get_script_json(html_blob)['page']['cards']:
        property_url = f'https://www.trulia.com{property_card["cardUrl"]}'
        logging.info(f'Searching apartment at URL {property_url}')
        property_blob = http_request.html_request(property_url)
        date_blob = property_blob.find('span', {'class': 'typeLowlight h6'})
        if date_blob is not None and exceeds_max_age(date_blob, max_age):
            logging.info(f'Maximum age: {max_age.strftime("%Y-%m-%d::%H:%M")} exceeded')
            return False
        crawled_apt = get_search_entry(property_blob, property_url)
        if not dbio.apt_in_database(crawled_apt):
            entry_list.append(crawled_apt)
    return True


def get_next_page(html_blob, base_url):
    script_json = get_script_json(html_blob)
    if script_json['page']['pagination']['lastPageUrl'] is None:
        return
    total_pages = int(get_script_json(html_blob)['page']['pagination']['pageButtonUrls'][-1]['pageNumber'])
    for i in range(2, total_pages + 1):
        yield base_url + f'{i}_p/'


def perform_search(initial_url, max_age, entry_list):
    # assert that it is actually sorted the correct way here.
    html_blob = http_request.html_request(initial_url)
    logging.info(f'Searching page {initial_url}')
    if html_blob is not None and search_page(html_blob, max_age, entry_list):
        for page in get_next_page(html_blob, initial_url):
            logging.info(f'Continuing search on page {page}')
            html_blob = http_request.html_request(page)
            if html_blob is None or not search_page(html_blob, max_age, entry_list):
                break
    logging.info(f'Search of url {initial_url} complete')
