#!/usr/bin/env python
import collections
import io
import os
import gzip
import argparse
import multiprocessing
import urllib.request

from collections import defaultdict
from datetime import datetime, timedelta
from functools import cmp_to_key, wraps
from timeit import default_timer as timer

DATE_INPUT_FORMAT = '%Y%m%d/%H'

BLACKLIST_URL = 'https://s3.amazonaws.com/dd-interview-data/data_engineer/wikipedia/blacklist_domains_and_pages'
PAGEVIEW_URL_FMT = 'https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{year}{month}{day}-{hour}0000.gz'
OUTPUT_FILE_FMT = '{year}{month}{day}-{hour}0000'

# default date to use in case of blank
DEFAULT_DATE = datetime.strftime(datetime.today(), DATE_INPUT_FORMAT)
# set to default output dir at the same level as wikipedia_pageview.py file.
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        start = timer()
        result = f(*args, **kw)
        end = timer()
        print('func:{} took: {:.2f} sec'.format(f.__name__, end-start))
        return result
    return wrap


class Ranker:
    '''
    Ranker class
    '''

    def __init__(self, blacklist, top, override, nprocessors, output_dir):
        self.blacklist = blacklist
        self.top = top
        self.override = override
        # max is 3 per Wikipedia file access limit!
        self.nprocessors = nprocessors
        self.output_dir = output_dir

    @staticmethod
    def child_process(input_queue, parse, rank, write, blacklist, top, override, output_dir):
        '''
        main child process unit that performs.
        1. retrieve date to work from input_queue.
        2. parse relevant url
        3. rank data
        4. write result

        :param input_queue:
        :param parse: func parse
        :param rank: func logic
        :param write: func write
        :param blacklist: dict, pages to skip
        :param top: int, top page# to return.
        :param override: boolean, override existing result or not.

        :return:
        '''

        while True:
            # get next available date info to process.
            date = input_queue.get()
            if date is None:
                # reached the end of work flows.
                return
            # unpack date parts.
            year, month, day, hour = date
            output_file = OUTPUT_FILE_FMT.format(year=year, month=month, day=day, hour=hour)
            full_path = os.path.join(output_dir, output_file)

            # if override is not set and output_file exists, just return.
            if not override and os.path.exists(full_path):
                print('File {} already exists! Skipping..'.format(full_path))
                continue

            # prepare full file url
            url = PAGEVIEW_URL_FMT.format(year=year, month=month, day=day, hour=hour)
            # parse url
            domain_page_counter = parse(url=url, blacklist=blacklist)
            # rank the data
            ranked = rank(domain_page_counter, top=top)
            # write out the result
            write(ranked, full_path)


    @staticmethod
    def _comparator(a, b):
        '''
        compares two (page, count) pairs to sort based on

        1. decreasing count &
        2. increasing page

        :param a: left side (page, count)
        :param b: right side(page, count)
        :return: 1,0,-1 based on above 1,2 criteria.
        '''
        if a[1] < b[1]:
            return 1
        elif a[1] > b[1]:
            return -1
        else:
            if a[0] < b[0]:
                return -1
            elif a[0] > b[0]:
                return 1
            else:
                return 0

    # @timing
    def parse(self, url, blacklist=None):
        '''
        parse remote gz.url from dumps.wikimedia.org into dictionary.

        :param url: full wikimedia.org url
        (ex https://dumps.wikimedia.org/other/pageviews/2019/2019-05/pageviews-2019-501-000000.gz)
        :param blacklist: optional blacklist dict: domain -> set(page)

        :return: domain_page_counter, dict[domain]->dict[page]->count
        '''

        blacklist = blacklist or self.blacklist
        domain_page_counter = defaultdict(dict)

        print('Process[{}] Reading: {}'.format(os.getpid(), url))
        response = urllib.request.urlopen(url)
        with gzip.GzipFile(fileobj=response) as pageview:
            with io.BufferedReader(pageview) as buffer:
                for line in buffer:
                    parts = line.split()
                    domain, page, count = parts[0].decode(), parts[1].decode(), int(parts[2])
                    # check against blacklisted domain/pages.
                    if domain in blacklist and page in blacklist[domain]:
                        # print('Skipping {}:{}'.format(domain,page))
                        continue
                    page_counter = domain_page_counter[domain]
                    page_counter[page] = page_counter.get(page, 0) + count

        return domain_page_counter

    # @timing
    def rank(self, domain_page_counter, top=None):
        '''
        ranks and sorts out the top pages per domain.

        :param domain_page_counter: dict[domain]->dict[page]->count
        :param top: top elements to return.
        :return: ranked: dict[domain]->[(page, count) ...]
        '''

        ranked = {}
        top = top or self.top

        print('Process[{}] Ranking..'.format(os.getpid()))
        # rank & sort top pages per domain.
        for domain, page_counter in domain_page_counter.items():
            # print('processing: {}'.format(domain))
            ranked[domain] = sorted(page_counter.items(), key=cmp_to_key(Ranker._comparator))[:top]

        return ranked

    # @timing
    def write(self, ranked, output_file):
        '''
        writes ranked contents into output file.
        format:
            domain
                count:# page:page
                ...
            ...

        :param: ranked: dict[domain]->[(page, count) ...]
        :param output_file: full path to output file.
        '''

        try:
            print('Process[{}] Writing: {}'.format(os.getpid(), output_file))

            # create dir if doesn't exists.
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # overwrite previous file if exists.
            with open(output_file, 'w') as of:
                for domain in sorted(ranked.keys()):
                    of.write('{}\n'.format(domain))
                    for count, page in ranked[domain]:
                        of.write('\tcount:{} page:{}\n'.format(page, count))
            print('Process[{}] Finished writing..'.format(os.getpid()))
        except Exception as e:
            print('Failed writing {}! Error:{}'.format(output_file, e))

    def process(self, start_date, end_date):
        '''
        Main logic. Creates processes, feeds inputs, and terminates.

        :param start_date, datetime
        :param end_date, datetime
        '''
        print('Processing {} - {} top:[{}] override:[{}] nprocessors:[{}] output_dir:[{}]'.format(
            start_date, end_date, self.top, self.override, self.nprocessors, self.output_dir
        ))

        # shared work queue
        input_queue = multiprocessing.Queue()
        workers = []

        # create separate Processors upfront.
        for _ in range(self.nprocessors):
            process = multiprocessing.Process(target=Ranker.child_process,
                                              args=(input_queue,
                                                    self.parse, self.rank, self.write,
                                                    self.blacklist, self.top,
                                                    self.override, self.output_dir))
            process.start()
            workers.append(process)

        date_ranges = generate_date_range(start_date, end_date)
        # Feed date ranges. None acts as indicator of exit one Process.
        for date in date_ranges + [None] * self.nprocessors:
            input_queue.put(date)

        # wait for all the workers exits.
        for worker in workers:
            worker.join()


def generate_date_range(start_date, end_date):
    '''
    generate (year, month, day, hour) points from start_date to end_date.

    :param start_date, datetime
    :param end_date, datetime
    :return: [(year, month, day, hour) ...] points
    '''
    date, date_ranges = start_date, []
    print('Generating date points from {} to {}'.format(start_date, end_date))

    fmt = '{:02d}'
    while date <= end_date:
        date_ranges.append((date.year, fmt.format(date.month), fmt.format(date.day), fmt.format(date.hour)))
        date += timedelta(hours=1)
    return date_ranges


def read_blacklist():
    '''
    read blacklist url from s3 wikipedia link (BLACKLIST_URL)

    :return: blacklist_dict[domain]->{page...}
    '''

    print('Reading blacklist..')
    blacklist_dict = defaultdict(set)

    try:
        with urllib.request.urlopen(BLACKLIST_URL) as response:
            for line in response:
                parts = line.strip().split()
                # skip those lines without any domain parts.
                if len(parts) < 2:
                    continue
                blacklist_dict[parts[0].decode()].add(parts[1].decode())
    except Exception as e:
        print('Error while reading s3 black list link: {}. \nIgnoring to use blacklist.'.format(e))
        blacklist_dict = defaultdict(set)

    return blacklist_dict


def prompt():
    '''
    Input prompt to retrieve parameters.

    E.g> ./wikipedia_pageview.py -s -d path_to_output_dir -o
            -> run current date/hour point and write on output_dir(override previous output).
         ./wikipedia_pageview.py -s 20190514/12 -e 20190514/15 -n 3 -d path_to_output_dir
            -> run 20190514/12 to current date/hour points using 3 child processes and write on output_dir.
    '''

    parser = argparse.ArgumentParser(description='Wikipedia pageview ranker')
    parser.add_argument('-s', '--start_date', default=DEFAULT_DATE, help='start date in yyyyMMdd/HH')
    parser.add_argument('-e', '--end_date', default=DEFAULT_DATE, help='end date in yyyyMMdd/HH')
    parser.add_argument('-t', '--top', type=int, default=25, help='top # pages to return. default:25')
    parser.add_argument('-o', '--override', action='store_true', help='override previously calculated results. default=False')
    parser.add_argument('-n', '--nprocessors', type=int, default=1, help='# of processors to use. default:1')
    parser.add_argument('-d', '--output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help='path to output dir')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, DATE_INPUT_FORMAT)
    end_date = datetime.strptime(args.end_date, DATE_INPUT_FORMAT)
    if start_date > end_date:
        raise ValueError('start_date {} > end_date {} '.format(start_date, end_date))

    return start_date, end_date, args.top, args.override, args.nprocessors, args.output_dir


import heapq


def build_host_map(host_to_listings, listings):

    for listing in listings:
        mheap = host_to_listings.get(listing[0], collections.deque())
        heapq.heappush(mheap, (listing[1], listing[0], listing[2]))
        host_to_listings[listing[0]] = heapq
    return host_to_listings


def build_page_heap(host_to_listings):
    page_heap = collections.deque()
    for host in host_to_listings.keys():
        heapq.heappush(page_heap, host_to_listings[host].popleft())
    return page_heap


def get_next(host_to_listings, page_heap):
    listing = heapq.heappop(page_heap)
    host = listing[1]

    # did we exhausted this host?
    if not host_to_listings[host]:
        host_to_listings.pop(host)
    else:
        heapq.heappush(page_heap, host_to_listings[host].popleft())

    return listing


def paginate(listings, page_size):
    # listings -> [ (hostid, score, name), (hostid, score, name) ... ]
    host_to_listings = build_host_map(listings)
    page_heap = build_page_heap(host_to_listings)

    page, pages, temps = [], [], collections.deque()
    hosts = set()
    unique_hosts = len(host_to_listings.keys())

    # there are items left to add.
    while page_heap:

        listing = get_next(host_to_listings, page_heap)
        host = listing[1]
        if host in hosts:
            temps.append(listing)
        else:
            hosts.add(host)
            page.append(listing)

        # check if page got all the hosts.
        if len(hosts) == unique_hosts:
            # first append all set side listings.
            while temps and len(page) < page_size:
                page.append(temps.popleft())

            while page_heap and len(page) < page_size:
                listing = get_next(host_to_listings, page_heap)
                page.append(listing)

        # reset page
        if len(page) == page_size:
            pages.append(page)
            page = []
            hosts = set()
            # add back previously accumulated temp items.
            # temps are already sorted and is in higher priority than page_heap items.
            host_to_listings = build_host_map(host_to_listings, temps + page_heap)
            temps = []
            unique_hosts = len(host_to_listings.keys())
            page_heap = build_page_heap(host_to_listings)

    if page:
        pages.append(page)

    # return list of lists(page)
    return pages


if __name__ == '__main__':
    # start of the program.
    start_date, end_date, top, override, nprocessors, output_dir = prompt()
    # read in blacklist dict.
    blacklist = read_blacklist()
    # create Ranker and start processing.
    ranker = Ranker(blacklist=blacklist, top=top, override=override, nprocessors=nprocessors, output_dir=output_dir)
    ranker.process(start_date, end_date)
