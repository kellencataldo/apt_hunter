import datetime as dt
import argparse
import sys
import logging
import json
import threading
import time
import os

import dbio
import post_processing
import email_handler
import apts_dot_com
import hotpads
import zillow


MAX_RUNTIME = 60 * 10

domain_handlers = {'apartments.com': apts_dot_com.perform_search,
                   'zillow': zillow.perform_search,
                   'hotpads': hotpads.perform_search}


def search_loop(domain, urls, max_age, entry_list):
    logging.info(f'Launched thread crawling domain: {domain}')
    start_time = dt.datetime.now()
    for search_url in urls:
        domain_handlers[domain](search_url, max_age, entry_list)
    logging.info(f'Ending crawler: {domain} runtime: {(dt.datetime.now() - start_time).seconds}s')


def start_crawler(args_tuple):
    thread_handle = threading.Thread(target=search_loop, name=args_tuple[0], args=args_tuple, daemon=True)
    thread_handle.start()
    return thread_handle


def wait_on_threads(thread_list):
    wait_time = MAX_RUNTIME
    for thread_handle in thread_list:
        start_time = time.time()
        thread_handle.join(timeout=wait_time)
        wait_time = wait_time - (time.time() - start_time) if wait_time > 0 else wait_time
        wait_time = 0 if wait_time < 0 else wait_time
        if thread_handle.is_alive():
            logging.error(f'Thread {thread_handle.name} exceeded max runtime value')


def convert_datetime(datetime_str):
    try:
        return dt.datetime.strptime(datetime_str, '%Y-%m-%d::%H:%M')
    except ValueError:
        raise argparse.ArgumentTypeError('Datetime conversion error')


def main():
    start_time = dt.datetime.now()

    parser = argparse.ArgumentParser(description='Let\'s just get this over with')
    parser.add_argument('--logging', metavar='level', type=str.upper, help='set logging level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='ERROR')
    parser.add_argument('--oldest', metavar='YYYY-mm-dd::HH:MM', type=convert_datetime,
                        help='Set the maximum post age of apartment entries to process')
    parsed_args = parser.parse_args()

    logging_int = getattr(logging, parsed_args.logging)
    log_file = os.path.join(os.environ['LOG_PATH'], f'{start_time.strftime("%m-%d-%Y")}.log')

    logging.basicConfig(filename=log_file, filemode='w', level=logging_int,
                        format='%(filename)s:%(lineno)d:%(threadName)s::%(message)s')
    logging.info(f'Logging started {start_time.strftime("%H:%M:%S")}')

    with open(os.environ['DATA_PATH'], "r") as config_file:
        json_blob = json.load(config_file)

    max_age = parsed_args.oldest
    if max_age is None:
        last_run_str = dbio.get_last_run()
        max_age = dt.datetime.strptime(last_run_str, '%Y-%m-%d::%H:%M') if last_run_str is not None\
            else dt.datetime(dt.MINYEAR, 1, 1)
    logging.info(f'Max age for posts: {max_age.strftime("%Y-%m-%d::%H:%M")}')

    domains = json_blob['domains']
    entry_list = []
    thread_list = [start_crawler((domain, urls, max_age, entry_list)) for domain, urls in domains.items()]
    wait_on_threads(thread_list)

    # do this here so that on an unsuccessful run the date is not set
    if not parsed_args.noset:
        dbio.set_last_run(start_time.strftime("%Y-%m-%d::%H:%M"))

    post_processing.post_process_entries(entry_list, json_blob['post_processing'])
    email_str = '\n\n'.join(str(entry) for entry in entry_list)

    email_handler.send_emails(json_blob['emails'], email_str, start_time)

    end_time = dt.datetime.now()
    logging.info(f'Logging ended: {end_time.strftime("%Y-%m-%d::%H:%M:%S")}'
                 f'runtime: {(end_time - start_time).seconds}s')
    logging.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
