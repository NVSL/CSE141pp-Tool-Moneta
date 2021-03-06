edges_test = []
with open('basic_blocks/format_graph', 'r') as f:
    lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip().split(', ')
        i+=1
        next_line = lines[i]
        i+=1
        count = int(next_line)
        disas = ''.join(lines[i:i+count])
        i+=count
        edges_test.append([line[0], line[1], disas])

from graphviz import Digraph

def gen_dot_graph2(edges):
    dot = Digraph(comment='Example')
    vertices = set()
    vertex_map = {}
    for edge in edges:
        vertices.add(edge[0])
        vertices.add(edge[1])
        vertex_map[edge[0]] = edge[2]
    
    for vertex in vertices:
        disas = vertex
        if vertex in vertex_map:
            disas = vertex_map[vertex]
        dot.node(vertex, disas)
        print(vertex, disas)

    for edge in edges:
        dot.edge(edge[0], edge[1])
        
    dot.render('test-dot2', view=True)
