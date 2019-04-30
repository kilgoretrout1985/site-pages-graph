import sys
import os.path
import csv
import concurrent.futures

import url as mozurl
import requests
import networkx as nx

from lib.link_helpers import find_links, normalize_links, filter_links, \
                             is_internal_link


MAX_THREADS = 20


def get_url(url: str) -> requests.Response:
    try:
        response = requests.get(url, timeout=5)
        return (url, response, None)
    except Exception as e:
        return (url, None, e)


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
            results = list(executor.map(get_url, urls))

        for current_url, response, exc in results:
            try:
                if exc is not None:
                    raise exc
                
                if response.status_code > 499:
                    response.raise_for_status()
                
                # check for redirect
                redirect_to = None
                redirect_status = None
                if response.history \
                and response.history[0].status_code in (301, 302):
                    redirect_to = response.url
                    redirect_status = response.history[0].status_code
                
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
                if todo_urls[current_url] > 5:  # stop trying
                    # write error info
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

            links = find_links(response.text)
            links = normalize_links(links, current_url)
            links = filter_links(links, current_url)
            # add redirect to crawl and count it as a linked page from current page
            if redirect_to is not None \
            and is_internal_link(redirect_to, current_url):
                links.append(redirect_to)

            for link in links:
                # add newly discovered for the job
                if link not in done_urls:
                    todo_urls[link] = 0
                # add to graph
                graph.add_edge(current_url, link)


    # prepare the results and write them
    host = mozurl.parse(start_url).host
    out_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

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
    
    # write csv
    csv_file = os.path.join(out_d, host+'.csv')
    with open(csv_file, mode='w') as csv_f:
        csv_writer = csv.writer(csv_f)
        csv_writer.writerow([
            'url',
            'status',
            'clicks from /',
            'internal links to url',
            'url redirects to'
        ])
        for url in done_urls:
            csv_writer.writerow([
                url,
                done_urls[url]['status'],
                done_urls[url]['clicks'],
                done_urls[url]['internal_links'],
                done_urls[url]['redirect_to'],
            ])
    print("Saved csv table to %s" % csv_file)
