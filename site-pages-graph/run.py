import sys
import os.path
import csv

import url
import requests

from lib.graph import Graph
from lib.link_helpers import find_links, normalize_links, filter_links, \
                             is_internal_link


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("Run this file with site root url like:")
        print("python3 %s https://mysite.com/" % sys.argv[0])
        sys.exit(0)

    graph = Graph({})
    start_url = str(url.parse( sys.argv[1] ).defrag().abspath())  # start url /
    todo_urls = [(start_url, 0),]  # list of tuples (url, error_count)
    done_urls = {}  # save info about processed urls here

    while True:
        try:
            current_url, current_url_errors = todo_urls.pop(0)
        except IndexError:
            break  # all done
        
        if current_url in done_urls:
            continue  # was already
        
        try:
            response = requests.get(current_url, timeout=5)
            
            if response.status_code > 499:
                response.raise_for_status()
            
            # check for redirect
            redirect_to = None
            redirect_status = None
            if response.history \
            and response.history[0].status_code in (301, 302):
                redirect_to = response.url
                redirect_status = response.history[0].status_code
            
            done_urls[current_url] = {
                'status': redirect_status if redirect_status is not None \
                                else response.status_code,
                'redirect_to': redirect_to,
            }
            print("Received %s" % current_url)
        except IOError as e:
            current_url_errors += 1
            if current_url_errors < 5:
                # retry later
                todo_urls.append((current_url, current_url_errors))
            else:
                # write error info
                done_urls[current_url] = {
                    'status': response.status_code,
                    'redirect_to': None,
                }
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
                todo_urls.append((link, 0,))
            # add to graph
            graph.add_edge(current_url, link)


    # prepare the results and write them
    host = url.parse(start_url).host
    out_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

    # save graph
    graph_file = os.path.join(out_d, host+'.pickle')
    graph.save_to_file(graph_file)
    print()
    print("Graph saved to %s" % graph_file)

    # compute clicks from graph one time for csv and sqlite
    print("Working with graph. This can be slow. Wait for a while.")
    c = 0
    for url in done_urls:
        # clicks to this page from homepage
        done_urls[url]['clicks'] = len(graph.find_shortest_path(start_url, url)) - 1
        # internal link to this page from other pages
        internal_links = 0
        for node in graph.g:
            if node != url and url in graph.g[node]:
                internal_links += 1
        done_urls[url]['internal_links'] = internal_links
        # print to show work is going
        c += 1
        if (c % 10) == 0:
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
