import numpy as np
from collections import namedtuple
import math
import networkx as nx

J = np.array([[0.0, -1.0], [1.0, 0.0]])     #for perpendiculars

ARCS = {}   #dictionary mapping a roundabout road ID to its Arc tuple

'''
Arc is a lightweight immutable tuple that stores geometry of circular road
center = 2D circle center
radius = radius of circle
phi0 = starting angle around the circles center
sigma = rotation direction, +1 counter clockwise
length = physical arc length of this segment
'''

Arc = namedtuple('Arc', 'center radius phi0 sigma length')


def ring_points(arc, x, d=0.0):
    # d = lane offset
    #Points ont he ring for distances x

    phi = arc.phi0 + arc.sigma * np.clip(x, 0.0, arc.length) / arc.radius
    # np.clip filter and makes sure all values btw 0.0 and the arc length
    # divifing by arc.radius converts the distance into angle in radian
    # multiplying by arc.sigma applies the direction aand adds to arc.phi0

    return arc.center + np.column_stack((np.cos(phi), np.sin(phi))) * (arc.radius - arc.sigma * d)
    # np.column_stack, stacks the cos and sin of phi in a 2D matrix
    # 2nd bracket accoutns for changing radius for lanes
    # adding this to center gives th epoints from origin to circles center

def ring_pose(arc, x, d):
    # calculates position, heading and normal for car at x meters

    phi = arc.phi0 + arc.sigma * min(max(x, 0.0), arc.length) / arc.radius
    #finds the angle for scalar distance clamped within the arc lenght and 0 and adds to phi

    radial = np.array([math.cos(phi), math.sin(phi)])
    #finds unit vector pointing outward from the center at this angle

    heading = arc.sigma * np.array([-radial[1], radial[0]])
    #rotates UnitVEc to 90 and sigma for direction

    normal = -arc.sigma * radial
    # perpendicualr normal vector with mathcign sign

    return arc.center + radial * (arc.radius - arc.sigma * d), heading, normal
    #return cars position, dorward heading and sideways normal

def _is_roundabout(data):
    j = data.get('junction')
    if isinstance(j, list):
        j = j[0]
    return j == 'roundabout'

def build_ring_arcs(graph, screen_nodes, tol=0.15):
    '''Gives ({(u, v): Arc}, [(centre, radius, node_set)]) for each roundabout'''
    edges = []
    for u, v, data in graph.edges(data=True):
        if _is_roundabout(data) and u != v:
            if u in screen_nodes and v in screen_nodes:
                edges.append((u,v))

    arcs, rings = {}, []

    #nx.graph makes an undirected graph from roundabout edges
    #nx.connected_component groups connected nodes onto seperate sets
    for comp in nx.connected_components(nx.Graph(edges)):
        #circle needs atleast 3 points
        if len(comp) < 3:
            continue

        nodes = sorted(comp) #sorts the node IDs for consistent order
        P = np.array([screen_nodes[n][0] for n in nodes], dtype=float)

        # np.column_stack makes a matrix of [2*x, 2*y,1]
        # np.ones makes a array a 1
        (cx, cy, k) , *_ = np.linalg.lstsq(np.column_stack((2 * P, np.ones(len(P)))), (P ** 2).sum(1), rcond=None)

        center = np.array([cx, cy])
        radius = math.sqrt(k + center @ center)
        #center @ center finds the dot product. so sum of their squares

        # skips the group is error more then 15% of radius
        # np.abs(np.linalg.norm(P - center, axis=1) - radius) => finds th eradius and finds th emax error
        if np.abs(np.linalg.norm(P - center, axis=1) - radius).max() > tol * radius:
            continue

        phi = {n: math.atan2(p[1] - cy, p[0] - cx) for n, p in zip(nodes, P)}
        #finds each nodes angle in rad relative to circles center

        es = [(u, v) for u, v in edges if u in comp]
        #filters edges to keep only those conected to this roundabout

        step = np.array([(phi[v] - phi[u] + math.pi) % (2 * math.pi) - math.pi for u, v in es])
        # computes the angle change for each edge btw +pi and -pi

        sigma = 1.0 if step.sum() >= 0 else -1.0
        #sums the signed steps, +ve counter, -ve clockwise

        sweep = (sigma * np.array([phi[v] - phi[u] for u, v in es])) % (2 * math.pi)
        #find the positive angle btw 0 to 2pi for each segment in the correct direction

        if abs(sweep.sum() - 2 * math.pi) > 0.3:
            continue

        for (u, v), s in zip(es, sweep):
            arcs[(u,v)] = Arc(center, radius, phi[u], sigma, radius * s) #creates an arc namestuple
        rings.append((center, radius, comp)) #stores the ring
    return arcs, rings