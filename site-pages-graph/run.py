import sys
import os.path
import concurrent.futures
from itertools import repeat

import url as mozurl
import requests
import networkx as nx

from settings import MAX_THREADS, NETWORK_TIMEOUT
from lib.output import write_csv, write_sqlite
from lib.link_helpers import find_links, normalize_links, filter_links, \
                             is_internal_link


def get_url(url: str, timeout: int = 30) -> tuple:
    try:
        response = requests.get(url, timeout=timeout)
        return (url, response, None)
    except Exception as e:
        return (url, None, e)


def find_redirect(response: requests.Response) -> tuple:
    redirect_to = None
    redirect_status = None
    if response.history \
    and response.history[0].status_code in (301, 302):
        redirect_to = response.url
        redirect_status = response.history[0].status_code
    return (redirect_to, redirect_status)


def parse_links(response: requests.Response, url: str) -> list:
    links = find_links(response.text)
    links = normalize_links(links, url)
    links = filter_links(links, url)
    
    # add redirect to crawl and count it as a linked page from current page
    redirect_to = find_redirect(response)[0]
    if redirect_to is not None and is_internal_link(redirect_to, url):
        links.append(redirect_to)
    
    return links


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("Run this file with site root url like:")
        print("python3 %s https://mysite.com/" % sys.argv[0])
        sys.exit(0)

    graph = nx.DiGraph()
    start_url = str(mozurl.parse( sys.argv[1] ).defrag().abspath())  # start url /
    todo_urls = { start_url: 0, }  # dict { url: error_count }
    done_urls = {}  # save info about processed urls here

    while True:
        urls = [x for x in todo_urls.keys() if x not in done_urls]
        if not urls:
            break  # all done

        threads_count = min(MAX_THREADS, len(urls))
        with concurrent.futures.ThreadPoolExecutor(threads_count) as executor:
            results = list(executor.map(
                get_url, 
                urls, 
                repeat(NETWORK_TIMEOUT, times=len(urls))
            ))

        for current_url, response, exc in results:
            try:
                if exc is not None:
                    raise exc
                if response.status_code > 499:
                    response.raise_for_status()
                
                redirect_to, redirect_status = find_redirect(response)
                # write data
                done_urls[current_url] = {
                    'status': redirect_status if redirect_status is not None \
                                    else response.status_code,
                    'redirect_to': redirect_to,
                }
                # clean up on successful retrieve
                del todo_urls[current_url]
                print("Processed %s" % current_url)
            except Exception as e:
                # value of a dict is number of tries to get the url
                todo_urls[current_url] += 1
                # stop trying and write error info
                if todo_urls[current_url] > 5:
                    try:
                        status = response.status_code
                    except AttributeError:  # response can be None
                        status = 0
                    done_urls[current_url] = {
                        'status': status,
                        'redirect_to': None,
                    }
                    del todo_urls[current_url]
                print("Error at %s: %s" % (current_url, str(e)))
                continue
        
            # every page (even with no links to others) is a node in a graph
            graph.add_node(current_url)

            links = parse_links(response, current_url)
            for link in links:
                # add newly discovered for the job
                if link not in done_urls:
                    todo_urls[link] = 0
                # add to graph
                graph.add_edge(current_url, link)


    # compute clicks from graph one time for csv and sqlite
    print("Working with graph. This can be slow. Wait for a while.")
    c = 0
    for url in done_urls:
        # clicks to this page from homepage
        done_urls[url]['clicks'] = nx.algorithms.shortest_path_length(
                                        graph, source=start_url, target=url)
        
        # internal link to this page from other pages
        internal_links = 0
        for node in graph:
            if node != url and url in graph[node]:
                internal_links += 1
        done_urls[url]['internal_links'] = internal_links
        
        # print to show work is going
        c += 1
        if (c % 3) == 0:
            print(".", sep='', end='', flush=True)
    print()
    
    # prepare the results and write them
    host = mozurl.parse(start_url).host
    out_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

    # write reports
    csv_file = os.path.join(out_d, host+'.csv')
    write_csv(csv_file, done_urls)
    print("Saved csv table to %s" % csv_file)
    sqlite_file = os.path.join(out_d, host+'.sqlite3')
    write_sqlite(sqlite_file, done_urls)
    print("Saved sqlite db to %s" % sqlite_file)
