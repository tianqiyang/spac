from solve0 import algo0
from utils import is_valid_network, average_pairwise_distance
from helperFunctions import addNodes, removeNodes

def algo5(G):
    """
    remove and node from mst.
    """
    T = algo0(G.copy())
    allNodes = set(list(G.nodes))
    for _ in range(2):
        used = set(list(T.nodes))
        T = addNodes(G, T, allNodes - used)
        T = removeNodes(G, T)
    assert is_valid_network(G, T)
    return T