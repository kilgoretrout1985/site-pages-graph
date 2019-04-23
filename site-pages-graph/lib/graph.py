import pickle


# https://www.python-course.eu/graphs_python.php
# https://www.python.org/doc/essays/graphs/
class Graph(object):
    # graph stored in dict, like:
    # {
    #     # page: [pages, it, links, to],
    #     '/': set(['/today-news', '/about-us', '/news/smth-happened',]),
    #     '/news/smth-happened': set(['/', '/today-news']),
    #     '/about-us': set(['/', '/small-plain-popup-page']),
    #     '/today-news': set(['/news/smth-happened', '/']),
    #     '/small-plain-popup-page': set(),  # page has no links
    # }
    g = None

    def __init__(self, graph_dict=None):
        if not graph_dict:
            graph_dict = {}
        self.g = graph_dict

    def save_to_file(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.g, f)
    
    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return cls(data)

    def nodes(self):
        return list(self.g.keys())

    def edges(self):
        edges = []
        for node in self.g:
            for neighbour in self.g[node]:
                # TODO: sets are unordered, edge direction may be broken
                if set((neighbour, node)) not in edges:
                    edges.append( set((node, neighbour)) )
        return edges

    def add_node(self, node):
        if node not in self.g:
            self.g[node] = set()

    def add_edge(self, from_node, to_node):
        self.add_node(from_node)
        self.add_node(to_node)
        self.g[from_node].add(to_node)
    
    # https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
    # https://stackoverflow.com/questions/3601180/calculate-distance-between-2-nodes-in-a-graph
    def find_all_paths(self, start_node, end_node):
        if start_node == end_node:
            yield [start_node]
        queue = [(start_node, [start_node])]
        while queue:
            (node, path) = queue.pop(0)
            for next in self.g[node] - set(path):
                if next == end_node:
                    yield path + [next]
                else:
                    queue.append((next, path + [next]))
    
    def find_shortest_path(self, start_node, end_node):
        try:
            return next(self.find_all_paths(start_node, end_node))
        except StopIteration:
            return None

    def __str__(self):
        s = "Nodes:\n"
        for node in self.g:
            s += "\t" + str(node) + "\n"
        s += "\nEdges:\n"
        for edge in self.edges():
            s += "\t" + str(edge) + "\n"
        return s
