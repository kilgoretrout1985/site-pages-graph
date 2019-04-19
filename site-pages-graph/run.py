import sys
from urllib.request import Request, urlopen

from lib.graph import Graph
from lib.helpers import find_links, normalize_links, filter_links


def get_undone(todo: dict) -> str:
    for key in todo:
        if not todo[key]:  # if not done
            return key
    return None


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("Run this file with site root url like:")
        print("python3 %s https://mysite.com/" % sys.argv[0])
        sys.exit(0)
    
    graph = Graph({})  # start empty graph
    url = str(url.parse( sys.argv[1] ).defrag().abspath())  # start url /
    todo = { url: False }  # url : is_done
    while True:
        current_url = get_undone(todo)
        if current_url is None:
            break
        
        print(current_url)
        html = urlopen(current_url, timeout=5)
        links = find_links(html)
        links = normalize_links(links, current_url)
        links = filter_links(links, current_url)
        
        # page with no links to other pages is still a node in a graph
        graph.add_node(current_url)
        todo[current_url] = True  # this link is done

        for link in links:
            # add newly discovered for the job
            if link not in todo:
                todo[link] = False
            # add to graph
            graph.add_edge(current_url, link)
            
    print(graph)