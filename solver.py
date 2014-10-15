#!/usr/bin/python
# -*- coding: utf-8 -*-
import constraint
import greedy
import graph

ofile = None

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    global ofile
    ofile = open("coloring.out", "w")
    ofile.write(input_data)
    ofile.flush()

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
        
    vertices = [graph.Vertex(i) for i in range(node_count)]
    for edge in edges:
        graph.insertEdge(vertices, edge)

    colors, maxColor, optimal = constraint.solve(vertices, node_count)

    # prepare the solution in the specified output format
    output_data = str(maxColor) + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, colors))
    
    ofile.close()

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print solve_it(input_data)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'

