import networkx as nx
import random


def mwd(G, weight='weight'):
    dom_set = set([])
    cost_func = dict((node, nd.get(weight, 1)) for node, nd in G.nodes(data=True))
    vertices = set(G)
    sets = dict((node, set([node]) | set(G[node])) for node in G)
    def _cost(subset):
        """ Our cost effectiveness function for sets given its weight
        """
        cost = sum(cost_func[node] for node in subset)
        return cost / float(len(subset - dom_set))
    while vertices:
        # find the most cost effective set, and the vertex that for that set
        dom_node, min_set = min(sets.items(),
                                key=lambda x: (x[0], _cost(x[1])))
        alpha = _cost(min_set)
        # reduce the cost for the rest
        for node in min_set - dom_set:
            cost_func[node] = alpha
        # add the node to the dominating set and reduce what we must cover
        dom_set.add(dom_node)
        del sets[dom_node]
        vertices = vertices - min_set
    return dom_set

def getComponents(G, needConnect):
    """
    G = nx.Graph()
    G.add_nodes_from([1,2,3,4,5,6])
    G.add_edges_from([(1,2),(2,3),(3,4),(3,5)])
    need = set()
    tree = set()
    needConnect = {1,2,3,4,5,6}
    input: G, needConnect
    return: [[6], [1, 2, 3, 4, 5]]
    """
    start = random.choice(list(needConnect))
    components = []
    while needConnect:
        needConnect.discard(start)
        part = [start]
        queue = [start]
        while queue:
            start = queue.pop()
            for e in set(G[start]):
                if e in needConnect:
                    needConnect.discard(e)
                    part.append(e)
                    queue.append(e)
        components.append(part)
        if len(needConnect) == 0:
            break
        start = random.choice(list(needConnect))
    return components

def findAllPath(G, components):
    pathDic = {}
    for i in range(len(components)):
        for j in range(i+1, len(components)):
            A = components[i]
            B = components[j]
            for x in range(len(A)):
                for y in range(len(B)):
                    if A[x] != B[y]:
                        pathDic[(A[x], B[y])] = nx.shortest_path(G, A[x], B[y])
    return pathDic

def sortPathHelper(x):
    try:
        path = pathDic[x]
        return sum([G[path[i]][path[i+1]]['weight'] for i in range(0, len(path)-1)])
    except:
        return float('inf')

def common_member(a, b): 
    a = set(a) 
    b = set(b) 
    if len(a.intersection(b)) > 0: 
        return True
    return False

def connectComponents(G, components):
    components = sorted(components, key=lambda x: len(x), reverse=True)
    pathDic = findAllPath(G, components)
    while len(components) > 1:
        path = sorted(pathDic, key=lambda x: sortPathHelper(x))[0]
        first = second = None
        start = path[0]
        end = path[1]
        for i in components:
            if start in i:
                first = i
            elif end in i:
                second = i
            if first != None and second != None:
                break
        newComponent = set()
        components.remove(first)
        for i in first:
            newComponent.add(i)
        components.remove(second)
        for i in second:
            newComponent.add(i)
        for i in pathDic[path]:
            newComponent.add(i)
        if len(components) == 0:
            return newComponent
        components.insert(0, list(newComponent))
        unique = True
        while unique:
            unique = False
            for i in range(len(components)):
                for j in range(i+1, len(components)):
                    if components[i] != components[j] and common_member(components[i], components[j]):
                        unique = True
                        a = components[i]
                        b = components[j]
                        components.remove(a)
                        components.remove(b)
                        components.append(list(set(a) | set(b)))
                        break
        pathDic = findAllPath(G, components)
    return components[0]

def buildTree(G, nodes):
    newG = nx.Graph()
    newG.add_nodes_from(nodes)
    for i in sorted(G.edges, key=lambda x: G[x[0]][x[1]]['weight']):
        if i[0] in nodes and i[1] in nodes:
            newG.add_edge(i[0], i[1], weight=G[i[0]][i[1]]['weight'])
    return nx.minimum_spanning_tree(newG, weight='weight')

def oneNode(G, nodes):
    onlyone = nx.Graph()
    onlyone.add_node(nodes[0])
    return onlyone

def addNodes(G, tree, rest):
    cur = average_pairwise_distance(tree)
    node = list(tree.nodes)
    added = False
    for i in rest:
        tree.add_node(i)
        for n in G[i]:
            if n in node:
                tree.add_edge(i, n)
                tree[i][n]['weight'] = G[i][n]['weight']
        tree = nx.minimum_spanning_tree(tree, weight='weight')
        if is_valid_network(G, tree):
            newdis = average_pairwise_distance(tree)
            if newdis > cur:
                tree.remove_node(i)
            else:
                cur = min(cur, newdis)
        else:
            tree.remove_node(i)
    return tree

def removeNodes(G, tree):
    nodes = list(tree.nodes)
    cur = average_pairwise_distance(tree)
    li = list(nodes)
    for i in nodes:
        li.remove(i)
        temp = buildTree(G.copy(), li)
        if len(temp.nodes) > 0 and is_valid_network(G, temp) and average_pairwise_distance(temp) < cur:
            cur = average_pairwise_distance(temp)
        else:
            li.append(i)
    return buildTree(G, li)