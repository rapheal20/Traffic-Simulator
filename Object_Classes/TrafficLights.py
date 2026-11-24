import numpy as np
from Active_Lists.ActiveList import ActiveSignals

GREEN, YELLOW, ALL_RED = 20.0, 3.0, 2.0
SLOT = GREEN + YELLOW + ALL_RED     #25s
CYCLE = 2 * SLOT    #50s


class TrafficLight:
    def __init__(self, node_id, phase_of, offset= 0.0):
        self.node_id = node_id
        self.phase_of = phase_of    #roadID : 0 or 1
        self.offset = offset        #shifts the clock so the junctions dont all chnage at once

    def state(self, road_id, t):
        phase = self.phase_of.get(road_id)      #always None if the road isnt in dictionary
        if phase is None:
            return 'green'
        rel = (t + self.offset - phase * SLOT) % CYCLE  #finds the seconds into my turn
        #wraps the time into 0 to 50 by modulo
        if rel < GREEN:
            return 'green'
        if rel < GREEN + YELLOW:
            return 'yellow'
        return 'red'

def build_signals(roads, nodes, rng):
    '''roads = ActiveRoads, nodes = ActiveNodes'''
    incoming = {}   #groups the roads by the nodes they meet at

    for road in roads.values():
        incoming.setdefault(road.EndNode, []).append(road)

    for nodeID, node in nodes.items():
        if node.Type != 'traffic_signals':
            continue
        arms = incoming.get(nodeID, [])
        if len(arms) < 2:
            continue
        #skips nodes with less then 2 roads

        ref = np.asarray(arms[0].UnitVector, dtype=float)
        phase_of = {}
        for road in arms:
            u = np.asarray(road.UnitVector, dtype=float)
            phase_of[road.road_id] = 0 if abs(ref @ u) >= 0.7071 else 1
            #@ find dot product of 2 direction vectors
            #0.7071 us cos45, any road within that is considered 1
            # parallel roads give +1, opposite -1 and perpedicular 0
        if len(set(phase_of.values())) < 2:
            continue
        #if no cross street then node is skipped
        ActiveSignals[nodeID] = TrafficLight(nodeID, phase_of, rng.uniform(0, CYCLE)) 