class Vertex:

    def __init__(self, graph):
        self.__graph = graph

    def get_neighbours(self):
        return self.__graph.get_neighbours(self)

    def get_graph(self):
        return self.__graph
