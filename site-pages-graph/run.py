import sys

import url
import requests

from lib.graph import Graph
from lib.link_helpers import find_links, normalize_links, filter_links


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
            
            print("Received %s" % current_url)
            done_urls[current_url] = {
                'status': response.status_code,
                'redirects_to': None,
            }
        except IOError as e:
            current_url_errors += 1
            if current_url_errors < 5:
                # retry later
                todo_urls.append((current_url, current_url_errors))
            else:
                # write error info
                done_urls[current_url] = {
                    'status': response.status_code,
                    'redirects_to': None,
                }
            print("Error at %s: %s" % (current_url, str(e)))
            continue
    
        # every page (even with no links to others) is a node in a graph
        graph.add_node(current_url)

        links = find_links(response.text)
        links = normalize_links(links, current_url)
        links = filter_links(links, current_url)        

        for link in links:
            # add newly discovered for the job
            if link not in done_urls:
                todo_urls.append((link, 0,))
            # add to graph
            graph.add_edge(current_url, link)
            
    print(graph)