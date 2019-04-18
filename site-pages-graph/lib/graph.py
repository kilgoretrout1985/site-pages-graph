# https://www.python-course.eu/graphs_python.php
# https://www.python.org/doc/essays/graphs/

class Graph(object):
    # graph stored in dict, like:
    # {
    #     # page: [pages, it, links, to],
    #     '/': ['/today-news', '/about-us', '/news/smth-happened',],
    #     '/news/smth-happened': ['/', '/today-news'],
    #     '/about-us': ['/', '/small-plain-popup-page'],
    #     '/today-news': ['/news/smth-happened', '/'],
    #     '/small-plain-popup-page': [],  # page has no links
    # }
    __g = None 

    def __init__(self, graph_dict=None):
        if not graph_dict:
            graph_dict = {}
        self.__g = graph_dict

    def nodes(self):
        return list(self.__g.keys())

    def edges(self):
        edges = []
        for node in self.__g:
            for neighbour in self.__g[node]:
                if set((neighbour, node)) not in edges:
                    edges.append( set((node, neighbour)) )
        return edges

    def add_node(self, node):
        if node not in self.__g:
            self.__g[node] = []

    def add_edge(self, edge):
        edge = set(edge)
        (node1, node2) = tuple(edge)
        if node1 in self.__g:
            self.__g[node1].append(node2)
        else:
            self.__g[node1] = [node2]
    
    # g.find_path("/", "/small-plain-popup-page")
    # ['/', '/about-us', '/small-plain-popup-page']
    # g.find_path("/small-plain-popup-page", "/")
    # None
    def find_path(self, start_node, end_node, path=None):
        if start_node not in self.__g:
            return None

        if not path:
            path = []
        path = path + [start_node]
        if start_node == end_node:
            return path

        for node in self.__g[start_node]:
            if node not in path:
                extended_path = self.find_path(node, end_node, path)
                if extended_path:
                    return extended_path
        return None
    
    # g.find_all_paths("/", "/news/smth-happened")
    # [ ['/', '/today-news', '/news/smth-happened'], ['/', '/news/smth-happened'] ]
    def find_all_paths(self, start_node, end_node, path=[]):
        if start_node not in self.__g:
            return []

        path = path + [start_node]
        if start_node == end_node:
            return [path]
        
        paths = []
        for node in self.__g[start_node]:
            if node not in path:
                extended_paths = self.find_all_paths(node, end_node, path)
                for p in extended_paths:
                    paths.append(p)
        return paths

    # g.find_shortest_path("/", "/news/smth-happened")
    # ['/', '/news/smth-happened']
    def find_shortest_path(self, start_node, end_node, path=None):
        if start_node not in self.__g:
            return None
        
        if not path:
            path = []
        path = path + [start_node]
        if start_node == end_node:
            return path
        
        shortest = None
        for node in self.__g[start_node]:
            if node not in path:
                newpath = self.find_shortest_path(node, end_node, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

    def __str__(self):
        s = "Nodes:\n"
        for node in self.__g:
            s += "\t" + str(node) + "\n"
        s += "\nEdges:\n"
        for edge in self.edges():
            s += "\t" + str(edge) + "\n"
        return s
