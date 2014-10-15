class Vertex:
    def __init__(self, id):
        self.originalId = id
        self.id = id
        self.neighbors = []

def insertEdge(vertices, edge):
    vertices[edge[0]].neighbors.append(vertices[edge[1]])
    vertices[edge[1]].neighbors.append(vertices[edge[0]])
