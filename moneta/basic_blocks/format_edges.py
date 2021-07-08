from graphviz import Digraph, Source

def read_edges(file_path="end_graph"):
    edges = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip().split(', ')
            i+=1
            next_line = lines[i]
            i+=1
            count = int(next_line)
            disas = lines[i] + "\n" + lines[i+1] + "\n" + ''.join(lines[i+2:i+count])
            i+=count
            edges.append([line[0], line[1], disas])
    return edges


def gen_dot_graph(edges, file_name="test_file"):
    dot = Digraph(comment='Example')
    vertices = set()
    vertex_map = {}
    for edge in edges:
        vertices.add(edge[0])
        vertices.add(edge[1])
        vertex_map[edge[0]] = edge[2].replace("\n", "\l")
    
    for vertex in vertices:
        disas = vertex
        if vertex in vertex_map:
            disas = vertex_map[vertex]
        dot.node(vertex, disas, shape="box")
        print(vertex, disas)

    for edge in edges:
        dot.edge(edge[0], edge[1])
        
    dot.render(file_name, view=True)
    return file_name

def display_graph(file_name="test_file"):
    return Source.from_file(file_name)
