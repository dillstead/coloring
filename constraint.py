import time
from collections import namedtuple
Problem = namedtuple("Problem", ['vertices', 'vertexCount'])
Solution = namedtuple("Solution", ['colors', 'maxColors'])
SearchState = namedtuple("SearchState", ['level', 'colors', 'maxColorUsed', 'domains', 'problem', 'data'])
searchStateId = 0

# Disclaimer: THIS IS NOT PRODUCTION LEVEL CODE

# Takes a graph and returns a coloring of the graph, the number of colors used, and whether or not it's
# optimal.
# vertices - graph stored as an adjacency list
# vertexCount - number of vertices
def solve(vertices, vertexCount):
    # The maximum degree is useful for two things:
    #  - an upper bound on variable domains
    #  - providing a good start node for the search, since it's the most constrained it means assignments to it will
    #    will prune the domain of more neighbors than a vertex of lesser degree
    vertices.sort(key = lambda vertex : len(vertex.neighbors), reverse = True)
    maxDegree = len(vertices[0].neighbors)
    for i in range(vertexCount):
        vertices[i].id = i
        
    problem = Problem(vertices, vertexCount)
    # Decision variables
    domains = [range(maxDegree + 1)] * (vertexCount - 1)

    # Start a trivial depth first search for a solution.
    data = {"best solution" : None, "node count" : 0, "start time" : int(time.time()), "progress start time" : int(time.time()), "max time" : 3600 * 5, "max progress time" : 30 * 60, "optimal" : 1}
    
    # Need to use stack because recursion depth was too deep for larger problems.
    searchStack = []
    # Break initial symmetry, the first node need only be the lowest color.
    searchState = SearchState(0, [0], 0, domains, problem, data)
    searchStack.append(searchState)
    while len(searchStack) > 0:
        searchState = searchStack.pop()
        solution = search(searchState.level, searchState.colors, searchState.maxColorUsed, searchState.domains, searchState.problem, searchState.data, searchStack)
        if solution != None:
            # Only save the solution if it's better than what we've found so far.
            if data["best solution"] == None or data["best solution"].maxColors > solution.maxColors:
                data["best solution"] = solution
                print("node count: %d" % (data["node count"]))
                print("Best solution so far: %d" % (data["best solution"].maxColors,))
    solution = data["best solution"]
    print("final node count: %d" % (data["node count"]))
    if solution != None:
        # Since we sorted the vertices in decreasing order of degree and the answer needs to be in the original order,
        # reorder them before returning.
        colors = solution.colors[:]
        for vertex in problem.vertices:
            colors[vertex.originalId] = solution.colors[vertex.id]
        return colors, solution.maxColors, data["optimal"]
    else:
        return [0], 0, 0

class PropagationResult:
    NotPropagated = 0
    Propagated = 1
    Violation = 2
    
# Takes already assigned colors, the remaining decision variables, the last vertex assigned a color,
# and its color and removes the color from the domains of its neighboring vertices. If a neighbor
# ends up with one color in its domain, continue propagating.  Returns NotPropagated if no propagation 
# is possible, Propagated if colors were removed from neighbors, and Violation if a vertex is forced to 
# be assigned the same color as one of its neighbors.
def propagateUnequalConstraints(colors, domains, vertex, color):
    #print("propagateUnequalConstraints")
    result = PropagationResult.NotPropagated
    if len(color) > 1:
        return result
    # Input is a single vertex that has a single color in its domain.  Propagate it.
    vertexStack = []
    # Stack contains (vertex, domain list of size 1)
    vertexStack.append((vertex, color))
    while len(vertexStack) > 0:
        vertex, color = vertexStack.pop()
        for neighbor in vertex.neighbors:
            if neighbor.id >= len(colors):
                # Looking forward
                # Remove color from neighbor's domain.
                # c   d        r
                # (x) (x)       (0) - violation
                # (x) (y)       (y) - prune y from neighbors
                # (x) (x, y)    (y) - prune y from neighbors
                # (x) (x, y, z) (y, z) - can't prune any further
                # (x) (y, z)    (y, z) - can't prune any further
                domain = domains[neighbor.id - len(colors)]
                try:
                    i = domain.index(color[0])
                    #print("removing color: " + str(color[0]) + " from domain: " + str(domain))
                    domain = domain[:]
                    domain.pop(i)
                    result = PropagationResult.Propagated
                    if len(domain) == 0:
                        return PropagationResult.Violation
                    if len(domain) == 1:
                        vertexStack.append((neighbor, domain))    
                    domains[neighbor.id - len(colors)] = domain
                except ValueError:
                    pass
            else:
                if color == colors[neighbor.id]: 
                    return PropagationResult.Violation
    return result
    
# Takes decision variable and removes from its domain all colors greater than maxColorUsed.        
def removeFromDomain(domain, maxColorUsed):
    #print("removing color: " + str(maxColorUsed) + " from domain: " + str(domain))
    newDomain = []
    for v in domain:
        if v <= maxColorUsed:
            newDomain.append(v)
    #print("resulting domain: " + str(newDomain))
    return newDomain
    
# Removes values from decision variable domains.  If any of the resulting domains are empty, return False else
# return True.
def filterDomains(maxColorUsed, domains, data):
    # If there are multiple colors greater than the maximum color assigned, remove all but the smallest
    # of them from the domain of the next decision variable.  This is another example of symmetry breaking.
    domains[0] = removeFromDomain(domains[0], maxColorUsed + 1)
    if len(domains[0]) == 0:
        #print("stop searching initial domain empty")
        return False
    # Trim values that are worse than the best known solution from all remaining domains.
    if data["best solution"] != None:
        maxColorUsed = data["best solution"].maxColors - 1
        for i in range(1, len(domains)):
            #print("remaining domain filter")
            domains[i] = removeFromDomain(domains[i], maxColorUsed)
            if len(domains[i]) == 0:
                #print("stop searching remaining domain empty")
                return False
    return True
    
# Depth-first search for solutions.  Takes a depth level, already assigned colors, the maximum colors
# used to this point, the remaining decision variables, the current search state, 
# information about the overall search, and the stack to push new state onto.
def search(level, colors, maxColorUsed, domains, problem, data, searchStack):
    #printSearchState(level, maxColorUsed, colors, domains)
    data["node count"] += 1
    timeStamp = int(time.time())
    # Print progress.
    if timeStamp - data["progress start time"] > data["max progress time"]:
        print("node count: %d" % (data["node count"]))
        print("progress...")
        data["progress start time"] = timeStamp
    
    # Stop if out of time and return the best solution found so far.
    if timeStamp - data["start time"] > data["max time"]:
        # Assume not optimal since time ran out.
        data["optimal"] = 0
        return data["best solution"]

    # This is an additional constraint that will prevent us from searching a branch of the tree if we've already used
    # more colors than the best known solution to this point.  This is very common in optimization problems.
    if data["best solution"] != None and maxColorUsed + 1 >= data["best solution"].maxColors:
        #print("stop searching already using more colors than best solution found")
        return None

    # If there are no more decision variables to assign, we have a solution, check it for validity and return. 
    if len(domains) == 0:
        obj = check(colors, maxColorUsed, problem, data)
        return Solution(colors, obj)
    else:
        # Filter domains of the remaining decision variables.
        if not filterDomains(maxColorUsed, domains, data):
            # Empty domain
            return None
        # Propagate initial unequal constraint
        #print("initial propagation")
        if propagateUnequalConstraints(colors, domains, problem.vertices[len(colors) - 1], [colors[-1]]) == PropagationResult.Violation:
            # Constraint violated
            #print("stop searching initial constraint violated")
            return None
        
        # Propagate any remaining unequal constraints that might be a result of filterDomains.
        #print("remaining propagation")
        i = 0
        while i < len(domains):
            if propagateUnequalConstraints(colors, domains, problem.vertices[i + len(colors)], domains[i]) == PropagationResult.Violation:
                return None
            i += 1
            
        # Continue the search.
        for v in reversed(domains[0]):
            # To generate new states, assigned colors to the next decision variable, adjust the maximum
            # number of colors used, and make a copy of the remaining decision variables.
            searchState = SearchState(level + 1, colors[:] + [v], max(maxColorUsed, v), domains[1:], problem, data)
            searchStack.append(searchState)
    return None

# Prints information about the search, indented to the proper level.
def printSearchState(level, maxColorUsed, colors, domains):
    indentation = ""
    for i in range(level):
        indentation += " "
    print(indentation + "level: " + str(level))
    print(indentation + "max color used: " + str(maxColorUsed))
    print(indentation + "colors: " + str(colors))
    print(indentation + "domains: ")
    for i in range(len(domains)):
        print(indentation + str(i) + ": " + str(domains[i]))

# Checks if a solution is feasible, if so, returns the number of colors used.
# Unnecessary since all solutions will be valid since we will have pruned the tree before 
# we get to an infeasible solution.
def check(colors, maxColorUsed, problem, data):
    colorsUsed = set()
    # A vertex's color must be different than all of it's neighbors.
    for vertex in problem.vertices:
        myColor = colors[vertex.id]
        colorsUsed.add(myColor)
        for neighbor in vertex.neighbors:
            neighborColor = colors[neighbor.id]
            assert(myColor != neighborColor)
    print("node count: %d" % (data["node count"]))            
    print("solution found with: " + str(maxColorUsed + 1) + " colors")
    assert(len(colorsUsed) == maxColorUsed + 1)
    # First color is 0, so maximum count is + 1.
    return maxColorUsed + 1
