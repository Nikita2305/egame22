class Vertex:

    def __init__(self, graph):
        self.graph = graph

    def get_neighbours(self):
        return self.graph.get_neighbours(self)
