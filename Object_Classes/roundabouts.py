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

    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for u, v in edges:
        parent[find(u)] = find(v)
    groups = {}
    for u, v in edges:
        groups.setdefault(find(u), []).append((u,v))

    arcs, rings = {}, []
    for es in groups.values():
        nodes = sorted({n for e in es for n in e})