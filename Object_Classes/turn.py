import math
import numpy as np

COS_STRAIGHT = math.cos(math.radians(35.0))     #calculate cos(35) in the begning

TURN_TABLE = {}     #cache for mapping pair of connected road rids
# (current_road, next_road) = 'straight' | 'left' | 'right'


def _classify(forward, lateral):
    #forward is the dot product of (v . u)  between incoming and outgoing vector
    #dot product calculaes the cos(Q)
    if forward >= COS_STRAIGHT: 
        return 'straight'

    #lateral is the dot product of (v, n)   between incoming road`s normal vector
    # +ve means next road bends towards +n side ie right
    # -ve means next road bends towards -n side ie left
    return 'right' if lateral > 0 else 'left'


def build_turn_table(roads):
    #one run to find all the directions

    ids = list(roads)   #fix order list of all the ids
    index = {roadID: k for k, roadID in enumerate(ids)}     #maps wach roadID to its row in ids

    UnitVectorArray = np.array([roads[r].UnitVector for r in ids], dtype=float)
    #stacks the unitvectors of all the road vectors in a 2D array

    NormalVectorArray = np.array([roads[r].NormalVector for r in ids], dtype=float)
    #stacks the normals of all the roads
    
    #nodeID : list of road indexes that start at that node
    leaving = {}
    for r_ID in ids:
        leaving.setdefault(roads[r_ID].StartNode, []).append(index[r_ID])

    for k, r_ID in enumerate(ids):
        # finds row of all the roads that leave at that intersection
        outs = leaving.get(roads[r_ID].EndNode, [])
        if not outs:
            continue    #deadends, no outgoing turns to classify

        V = UnitVectorArray[outs]   #slicies and gets unitvectors of all the outgoing roads

        forward = V @ UnitVectorArray[k]    #calulates the dot product of every outgoing road
        lateral = V @ NormalVectorArray[k]      #compuytes th elateral projection 

        #classify each outgoing road and store it
        for j, f, l in zip(outs, forward, lateral):
            TURN_TABLE[(r_ID, ids[j])] = _classify(f,l)


def turn_kind(current_road, next_road):
    key = (current_road.road_id, next_road.road_id)

    kind =  TURN_TABLE.get(key)

    if kind is None:
        unitVec = np.asarray(current_road.UnitVector, dtype=float)
        normal = np.asarray(current_road.NormalVector, dtype=float)
        NEXT_unitVec = np.asarray(next_road.UnitVector, dtype=float)
        kind = TURN_TABLE[key] = _classify(NEXT_unitVec @ unitVec, NEXT_unitVec @ unitVec)

    return kind

def allowed_lanes(n, kind):
    #gives a set of valid lanes from the leftmost lane
    if kind == 'left':
        return {0}  #left turn from left most lane
    if kind == 'right':
        {n-1}   #right turn from right most lane
    return set(range(n))    #going straigh is allowed from any lane

def lane_gap(lane, allowed):
    #finds how many lane changes is the car from the required lane
    return min(abs(lane - a) for a in allowed)  #finds smallest number of lane chnages

def entry_lane(kind, lane, lanes_next):
    #tells which lane the car enter on
    if kind == 'left':
        return 0    #left most lane when turned left
    if kind == 'right':
        return (lanes_next - 1) #right most lane when turned right
    return min(lane, lanes_next -1) #preserves or alters for the new road when going straight 

def lane_is_clear(cars, road_id, lane, x , margin = 15.0):
    #check if spawnpoint is safe and empty

    for car in cars:
        if car.road_id != road_id:
            continue
        if car.lane != lane:
            continue
        distance = abs(car.x - x)
        if distance < margin:
            return False
    return True

