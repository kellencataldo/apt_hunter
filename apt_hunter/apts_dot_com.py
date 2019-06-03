import datetime as dt
import logging
import json
import re

import dbio
import http_request


def get_next_page(html_soup, base_url):
    paging_div = html_soup.find(id='paging')
    if paging_div is None:
        return
    total_pages = int(paging_div.find_all('a')[-2].text)
    url_split = base_url.rfind('/')
    url_left_piece = base_url[:url_split + 1]
    sort_order = base_url[url_split + 1:]
    for i in range(2, total_pages + 1):
        yield url_left_piece + f'{i}/' + sort_order


def exceeds_max_age(freshness_blob, current_time, max_age):
    if freshness_blob.find('span', {'class': 'new'}) is not None:
        return False

    date_str = freshness_blob.find('span', {'class': 'lastUpdated'}).find('span').text
    date_match = re.match(r'([0-9]+) (min|hr|hrs|day|days|wk|wks) Ago', date_str)

    unit_str = date_match.group(2)
    unit_amount = int(date_match.group(1))

    if unit_str == 'min':
        current_time -= dt.timedelta(minutes=unit_amount)
    elif unit_str == 'hr' or unit_str == 'hrs':
        current_time -= dt.timedelta(hours=unit_amount)
    elif unit_str == 'day' or unit_str == 'days':
        current_time -= dt.timedelta(days=unit_amount)
    elif unit_str == 'wk' or unit_str == 'wks':
        current_time -= dt.timedelta(days=(unit_amount * 7))
    else:
        logging.error(f'Unhandled date time unit: {unit_str}, date string: {date_str}')
        return True
    logging.info(f'Freshness string: {date_str} converted time: {current_time.strftime("%Y-%m-%d::%H:%M")}')
    return current_time < max_age


def get_search_entry(json_blob):
    property_json = json.loads(json_blob)
    main_entity = property_json['mainEntity'][0]
    url = main_entity['url']
    title = main_entity['name']
    street_address = main_entity['address']['streetAddress']
    city = main_entity['address']['addressLocality']
    state = main_entity['address']['addressRegion']
    address = re.sub(r'([^0-9A-Za-z ,#]+)', '', ' '.join([street_address, city, state])).lower()
    description = main_entity['description']
    price = property_json['about']['offers']['highPrice']
    return dbio.ApartmentEntry(address, price, url, title, description)


def search_page(html_blob, max_age, entry_list):
    current_time = dt.datetime.now()
    logging.info(f'Current time: {current_time.strftime("%Y-%m-%d::%H:%M")}')
    for prop_article in html_blob.find('div', {'class': 'placardContainer'}).find_all('article'):
        freshness_blob = prop_article.find('span', {'class': 'listingFreshness'})
        if exceeds_max_age(freshness_blob, current_time, max_age):
            logging.info(f'Maximum age: {max_age.strftime("%Y-%m-%d::%H:%M")} exceeded')
            return False
        property_url = prop_article.find('a', {'class': 'placardTitle js-placardTitle'})['href']
        property_blob = http_request.html_request(property_url)
        json_blob = property_blob.find('script', {'type': 'application/ld+json'})
        crawled_apt = get_search_entry(json_blob.text)
        if not dbio.apt_in_database(crawled_apt):
            entry_list.append(crawled_apt)
    return True


def perform_search(initial_url, max_age, entry_list):
    html_blob = http_request.html_request(initial_url)
    logging.info(f'Searching page {initial_url}')
    if html_blob is not None and search_page(html_blob, max_age, entry_list):
        for page in get_next_page(html_blob, initial_url):
            logging.info(f'Continuing search on page {page}')
            html_blob = http_request.html_request(page)
            if html_blob is None or not search_page(html_blob, max_age, entry_list):
                break
    logging.info(f'Search of url {initial_url} complete')
