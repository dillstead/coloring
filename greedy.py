import time
import fpformat
import sys

# Best greedy solution
# 8     20     21     97     18     124
 
def getNextColor(vertex, colors, neighborColors, maxColor):
    for neighbor in vertex.neighbors:
        if colors[neighbor.id] != -1:
            # Mark this color as unusable for this vertex.
            if not neighborColors[colors[neighbor.id]]: 
                neighborColors[colors[neighbor.id]] = True
                
    # Find the smallest possible color to color this vertex or, if necessary, create a new one.
    colorToUse = -1
    for i in range(len(neighborColors)):
        if not neighborColors[i] and colorToUse == -1: 
            colorToUse = i
        neighborColors[i] = False
        
    if colorToUse == -1:
        # All colors in use, add a new one.
        neighborColors.append(False)
        colorToUse = maxColor
        maxColor += 1

    return colorToUse, maxColor

def solve(vertices, vertexCount):
    percent = vertexCount / 20
    if percent == 0:
        percent = 1
    
    colors = [-1 for i in range(vertexCount)]
    neighborColors = []
    maxColor = 0

    # Sort vertices in decreasing order of degree
    #vertices.sort(key = lambda vertex : len(vertex.neighbors), reverse = True)
    vertices.sort(key = lambda vertex : len(vertex.neighbors))
        
    i = 0
    start = time.time()
    for vertex in vertices:
        # Not colored, pick a color.
        colorToUse, maxColor = getNextColor(vertex, colors, neighborColors, maxColor)
        colors[vertex.id] = colorToUse
        if i % percent == 0:
            sys.stdout.write(fpformat.fix(time.time() - start, 3) + " ")
            start = time.time()
        i += 1
        
    sys.stdout.write("\n")
            
    return colors, maxColor, 0    
    