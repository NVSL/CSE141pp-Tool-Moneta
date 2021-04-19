import subprocess
from graphviz import Digraph
from cse142.settings import CFG_OUTPUT_DIR, CFG_TOOL_OUTFILE

def load_edges():
    edges = []
    with open(CFG_OUTPUT_DIR + CFG_TOOL_OUTFILE, 'r') as f:
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
            edges.append([line[0], line[1], disas])

    return edges


def generate_cfg(edges, outfile_path):
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

    for edge in edges:
        dot.edge(edge[0], edge[1])
        
    dot.render(outfile_path, view=True)
