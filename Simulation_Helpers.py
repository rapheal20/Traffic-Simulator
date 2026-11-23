import osmnx as ox

# ox.settings.use_cache = False
# ox.settings.log_console = False
#to stop it from writing cache into restructed dir(for executable)

import statistics as st
import numpy as np
import re
import os
import sys
import random
import uuid
import math
from Active_Lists.ActiveList import ActiveRoadsList, ActiveCarsNow
from Object_Classes.TrafficLights import ActiveSignals, build_signals
from Object_Classes.roads import roads
from Object_Classes.nodes import nodes
from Object_Classes.IDM_Car import Car
from Object_Classes.turn import lane_is_clear, allowed_lanes, lane_gap, entry_lane
from Object_Classes.roundabouts import build_ring_arcs, ring_pose, ARCS, YIELD_MAP, build_yield_map

A_LAT = 2.0 #acc drivers accept on a curve

# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.15 #in meters
DASH_length = 3
GAP_length = 3

DT = 0.1
#LANE CHANGING CONST.
LANE_SAFE_BRAKE = 4.0   #max braking to impose on new follower
LANE_GAIN = 0.3     #minimum benefit to change lane
LANE_COOLDOWN = 5.0

#LANE CHANGE FOR TURN CONST.
TURN_ZONE = 150.0   #distance where laen change begins for turn
TURN_WEIGHT = 3.0   #benefot of being 1 lane closer
LANE_COOLDOWN_TURN = 1.5    #shorter cooldown for turn lanechange

carWidth = 2
carlength = 4.5
DRIVE_SIDE = +1 #left hand traffic

#Roundabout Giveway const.
YIELD_LOOK = 80
T_CRIT = 3.5
T_FOLLOW = 1.5
V_MIN = 1.0

#Box Blocking Const.
BOX_LOOK = 60.0 #from how far is the exit space checked
BOX_MARGIN = 2.0    #extra space beyond the cars own lengh
BOX_PATIENCE = 12.0     #seconds a car waits before entering anyway


DEFAULT_LIMITS = {   # km/h, by OSM 'highway' tag
    'motorway': 100, 'trunk': 80, 'primary': 60,
    'secondary': 50, 'tertiary': 40, 'residential': 30,
}

def resource_path(relative_path):
  base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
  return os.path.join(base_path, relative_path)

def Make_Map(coordinates, radius):
    graph = ox.graph_from_point(coordinates, dist=radius, network_type='drive') # takes the center from the tuple and then takes a curcle of raduis 400m
    
    # graph = ox.load_graphml(resource_path('nyc_map.graphml')) #do avoid a crash in exe
    projectedGraph = ox.project_graph(graph) #converts the graph form latitide and longitude to XY coordiantes(needed for pygames)
    
    
    minX, minY = float('inf'), float('inf') #gives the valueof infinity
    maxX, maxY = float('-inf'),float('-inf')
    for node_id, data in projectedGraph.nodes(data=True):
        X_value = (data['x'])
        Y_value = (data['y'])

        if X_value > maxX:
            maxX = X_value
        if X_value < minX:
            minX = X_value

        if Y_value > maxY:
            maxY = Y_value
        if Y_value < minY:
            minY = Y_value

    mapWidth = maxX - minX
    mapHeight = maxY - minY

    ScreenWidth = 1000
    ScreenHeight = 1366
    margin = 50 #to make a border

    scale = min(((ScreenWidth - (2*margin))/mapWidth), ((ScreenHeight - (2*margin))/mapHeight))

    screen_nodes = {}
    '''
    screen_nodes = {
        3424545 : [(x, y), 4]
    }
    '''
    for node_id, data in projectedGraph.nodes(data=True):
        pixelX = margin + (data['x']-minX)*scale
        # takes the x coordinate, subtracts the minium X value to get the relative postion ie from 0 of the screen
        # multiplies iwth scale and adds margin to make sure it goes with the screen
        pixelY = margin + (data['y']-minY)*scale

        StreetsConnected = data['street_count']
        screen_nodes[node_id] = [(int(pixelX), int(pixelY)), StreetsConnected]


    return scale, projectedGraph, screen_nodes

def Final_Lane_Count(projectedGraph, screen_nodes):
    FinalLaneCounts = {}
    for u, v, data in projectedGraph.edges(data=True):
        if u in screen_nodes and v in screen_nodes:
            wayLanes = {}

            #replaced osmid with road name as the id was only unique for roads conencting a segment
            name = data.get('name') #every continous road segment shares the same osmid 
            LaneNo = data.get('lanes', 1)

            # isinstance checks if the given object is of the given datatype
            if isinstance(LaneNo, list):
                try:
                    LaneNo = int(LaneNo[0])
                except:
                    LaneNo = 1
            else:
                try:
                    LaneNo = int(LaneNo)
                except:
                    LaneNo = 1

            if isinstance(name, list):
                name = name[0]

            if name not in wayLanes:
                wayLanes[name] = []
            wayLanes[name].append(LaneNo)

            
            for name, laneList in wayLanes.items():
                MostCommonLanes = int(st.mode(laneList))
                FinalLaneCounts[name] = MostCommonLanes

    return FinalLaneCounts

def findSpeedLimit(data):
    speedlimit = data.get('maxspeed', None)
    if isinstance(speedlimit, list):
        speedlimit = speedlimit[0]
    
    if speedlimit:
        speed = re.search(r"\d+", str(speedlimit))
        value = float(speed.group(0)) if speed else 40
        speedLimit_KMH = round(value * 1.6) if "mph" in str(speedlimit) else round(value)
    else:
        roadtype = data.get('highway')
        if isinstance(roadtype, list):
            roadtype = roadtype[0]
        speedLimit_KMH = DEFAULT_LIMITS.get(roadtype, 40)

    return speedLimit_KMH

def Initialize_Map(coordinates, radius, ActiveNodesDict, NodesforRoad):
    scale, projectedGraph, screen_nodes = Make_Map(coordinates, radius)
    FinalLaneCounts = Final_Lane_Count(projectedGraph, screen_nodes)
    AvailableLocations = []
    # MAP SAVING

    '''ROADS'''
    RING_ARCS, _ = build_ring_arcs(projectedGraph, screen_nodes)

    for u, v, data in projectedGraph.edges(data=True):
        # Make sure both ends of the road exist in our screen dictionary
        if u in screen_nodes and v in screen_nodes:
            #Linear Algebra concept
            start_pos = screen_nodes[u][0]
            end_pos = screen_nodes[v][0]
            
            #np.array converts it into vector
            vector1 = np.array(start_pos, dtype=float)
            vector2 = np.array(end_pos, dtype=float)

            #vector subtraction so each element is subtracted from its corresponding element
            direction = vector2 - vector1

            # calculates its euclidean length, basically the hypotneous of it
            length = round(np.linalg.norm(direction),0)
            UnitVector = direction/length

            rotation_Matrix = np.array([[0,-1],[1,0]]) #2D vector whcih roates any value by 90 degrees counterclockwise
            normal = rotation_Matrix.dot(UnitVector) #does dot multiplication

            arc = RING_ARCS.get((u, v))
            if arc is not None:
                length = round(arc.length)
                _, UnitVector, normal = ring_pose(arc, 0.0, 0.0)

            Speed_Limit_KMH = findSpeedLimit(data)
            if arc is not None:
                Speed_Limit_KMH = min(Speed_Limit_KMH, max(15, round(3.6 * math.sqrt(A_LAT * arc.radius))))

            oneway = data.get('oneway', True)

            name = data.get('name')
            if isinstance(name,list):
                name = name[0]

            raw = FinalLaneCounts.get(name)

            if isinstance(raw, list):
                raw = raw[0]
            try:
                total = int(raw)
            except:
                total = 1
            LaneNo = max(1, total) if oneway else max(1, (total + 1)//2)

            uniqueID = str(uuid.uuid4())

            if u not in NodesforRoad:
                NodesforRoad[u] = []
            NodesforRoad[u].append(uniqueID)
            if v not in NodesforRoad:
                NodesforRoad[v] = []
            NodesforRoad[v].append(uniqueID)


            #if the road has a single lane it is considered minor and will be used for spawing cars
            if LaneNo < 2 or data.get('highway') != "motorway":
                if length >= 20 and arc is None:
                    AvailableLocations.append(uniqueID)
                
            newRoad = roads(
                roadID= uniqueID,
                coordinates= [vector1,vector2],
                roadLength= length,
                lanes= LaneNo,
                oneway= oneway,
                speedLimit= Speed_Limit_KMH,
                unitVec= UnitVector,
                normal=normal,
                startNode=u,
                endNode=v
            )

            newRoad.is_ring = arc is not None
            if arc is not None:
                ARCS[uniqueID] = arc

    '''NODES'''        

    for nodeID, nodeData in projectedGraph.nodes(data=True):
        if nodeID in screen_nodes:
            coordinates = screen_nodes[nodeID][0]
            roadNum = screen_nodes[nodeID][1]
            nodeType = nodeData.get('highway', None)
            if isinstance(nodeType, list):
                nodeType = 'traffic_signals' if 'traffic_signals' in nodeType else nodeType[0]
            connectedroads = NodesforRoad[nodeID]
            maxLanes = 0
            
            for roadID in connectedroads:
                road = ActiveRoadsList[roadID]
                laneNo = road.lanes if road.oneway else road.lanes * 2
                if laneNo > maxLanes:
                    maxLanes = laneNo
                    mainRoad = roadID
            nodes(
                ID=nodeID,
                coordinates=coordinates,
                roads=roadNum,
                type=nodeType,
                connections=connectedroads,
                maxLanes=maxLanes,
                mainRoad= mainRoad
            )

    for rID in ARCS:
        road = ActiveRoadsList[rID]
        for n in (road.StartNode, road.EndNode):
            ActiveNodesDict[n].MaxLanes = road.lanes


    '''SIGNAL'''
    for road in ActiveRoadsList.values():
        buf = ActiveNodesDict[road.EndNode].MaxLanes * LANE_WIDTH/2 #same as trim, used to stop car before
        road.stop_x = road.lenght if road.is_ring else max(road.lenght * 0.5, road.lenght - buf)     #adds new attribute

    build_signals(ActiveRoadsList, ActiveNodesDict, random.Random(1))
    build_yield_map(ActiveRoadsList)

    return scale, AvailableLocations

def SortInLanes(ActiveCarsNow):
    #clears all the lanes
    for roadOBJ in ActiveRoadsList.values():
        roadOBJ.cars_data = [[] for _ in range(roadOBJ.lanes)]

    #adds all the cars into their own road and lane
    for car in ActiveCarsNow:
        ActiveRoadsList[car.road_id].cars_data[car.lane].append(car)

    for road in ActiveRoadsList.values():
        for lane in road.cars_data:
            lane.sort(key=lambda c: c.x, reverse=True)
            #reverse so that index 0 is the car furthest away

def FindLeader(car, lane, i, road):
    #same road same lane
    if i > 0:
        lead = lane[i - 1]
        gap = (lead.x - lead.length) - car.x
        return gap, lead.v

    #next road of the route
    next_id = car.next_road_id
    if next_id is None:
        return None, 0.0

    next_Road = ActiveRoadsList[next_id]
    next_Lane = entry_lane(car.next_turn, car.lane, int(next_Road.lanes))
    cars_There = next_Road.cars_data[next_Lane]
    if not cars_There:
        return None, 0.0

    lead = cars_There[-1]
    gap = (road.lenght - car.x) + (lead.x - lead.length)
    return gap, lead.v
    
def gap_between(rear, front):
    return ((front.x - front.length) - rear.x)

def neighbours_in_lane(lane_list, x):
    leader = follower = None
    for other in lane_list:
        if other.x > x:
            leader = other  #updates to the closest car ahead
        else:
            follower = other    #first car behind the car
            break
    return leader, follower

def try_lane_change(car, road):
    lanes = road.cars_data
    limit = road.speed_limit
    current_lane = lanes[car.lane]
    i = current_lane.index(car) #index of car in the current lane

    allowed = allowed_lanes(len(lanes), car.next_turn)
    urg = turn_urgency(car, road)
    need_now = lane_gap(car.lane, allowed)  #0 = already in the lane

    if i > 0:
        gap = gap_between(car, current_lane[i-1])
        leader_v = current_lane[i-1].v
    else:
        gap, leader_v = None, 0.0

    a_now = car.compute_acceleration(limit, gap, leader_v)

    best_target = None
    best_progress = 0

    best_score = LANE_GAIN if (need_now == 0 or urg == 0.0) else 0.0
    safe_brake = LANE_SAFE_BRAKE + 2.0 * urg    #accept rougher brake when time is short


    for target in (car.lane-1, car.lane+1): #iterates through the neighbouring lanes
        if target < 0 or target >= len(lanes):  #checks if the lanes exit
            continue
        leader, follower = neighbours_in_lane(lanes[target], car.x)

        if leader:
            gap2, leader_v2 = gap_between(car, leader), leader.v
            if gap2 < car.profile.s0:   #if gap is less then minimum bumper gap fir th edriver
                continue
        else:
            gap2 , leader_v2 = None, 0.0

        a_new = car.compute_acceleration(limit, gap2, leader_v2)

        loss = 0.0
        if follower:
            gap_follower = gap_between(follower, car)
            if gap_follower < follower.profile.s0:
                continue
            if leader:
                a_follower_before = follower.compute_acceleration(limit, gap_between(follower, leader), leader.v)
            else:
                a_follower_before = follower.compute_acceleration(limit)
            a_follower_after = follower.compute_acceleration(limit, gap_follower, car.v)
            if a_follower_after < -safe_brake:
                continue
            loss = max(0.0, a_follower_before - a_follower_after)

        progress = need_now - lane_gap(target, allowed) 
        score = (a_new - a_now) - car.politeness * loss + TURN_WEIGHT * urg * progress
        if score > best_score:
            best_target, best_score, best_progress = target, score, progress

    if best_target is not None:
        current_lane.remove(car)
        target_lane = lanes[best_target]
        index = sum(1 for o in target_lane if o.x > car.x)
        target_lane.insert(index, car)
        car.lane = best_target
        car.lane_cooldown = LANE_COOLDOWN_TURN if (best_progress > 0 and urg > 0) else LANE_COOLDOWN
        car.history.clear()

def simulation_step(cars, dt, t):
    # t = current simulation time in sec
    SortInLanes(ActiveCarsNow)

    for car in cars:
        car.lane_cooldown = max(0.0, car.lane_cooldown - dt)

    for road in ActiveRoadsList.values():
        if len(road.cars_data) < 2:
            continue
        movers = [c for lane in road.cars_data for c in lane] #makes a list of all the cars
        for c in movers:
            if c.lane_cooldown == 0.0:
                try_lane_change(c, road)
    #deciding phase
    decisions = []
    for road in ActiveRoadsList.values():
        for lane in road.cars_data:
            for i, carOBJ in enumerate(lane):
                gap , leader_v = FindLeader(carOBJ, lane, i, road)
                carOBJ.observe(t, gap, leader_v)
                per_gap, per_leader_v = carOBJ.perceived()
                if gap is not None and gap < carOBJ.profile.s0:
                    per_gap, per_leader_v = gap, leader_v
                for obs in (signal_leader(carOBJ, road, t), yield_leader(carOBJ, road, t), box_leader(carOBJ, road, t)): 
                    if obs is not None and (per_gap is None or obs[0] < per_gap):
                        per_gap, per_leader_v = obs

                sig = signal_leader(carOBJ, road, t)
                if sig is not None and (per_gap is None or sig[0] < per_gap):
                    per_gap, per_leader_v = sig

                decisions.append((carOBJ, carOBJ.compute_acceleration(approach_limit(carOBJ, road), per_gap, per_leader_v)))

    for car, a in decisions:
        prev_x = car.x
        car.apply(a, dt)
        road  = ActiveRoadsList[car.road_id]
        light = ActiveSignals.get(road.EndNode)
        stop = getattr(road, "stop_x", None)
        if light and stop and prev_x < stop <= car.x and light.state(road.road_id, t) == "red":
            print("RED RUN", car.id, f"{car.v*3.6:.0f} km/h")
        car.update_route(ActiveRoadsList)

    cars[:] = [c for c in cars if not c.finished] #removes any cars that is finished

def signal_leader(car, road, t):
    light = ActiveSignals.get(road.EndNode)
    if light is None:
        return None #checks for light at end, if no light then dosnt stop
    state = light.state(road.road_id, t)
    if state == 'green':
        return None
    dist = getattr(road, 'stop_x', road.lenght) - car.x #getattr reads by name and falls back to a default
    if dist < 0.5:  #if its past this line then it just goes along to clear the juction
        return None
    if state == "yellow" and car.v **2/(2 * car.profile.b) > dist:  #if the car can stop comfortably then it stops else it goes through
        # d = (v^2 / 2b)    uses kinematics formual to find the decelration needed
        return None
    return dist, 0.0

def yield_leader(car, road, t):
    #this is for the giveway line at roundabout entry, acts like a red light if roundabout is busy
    feeders = YIELD_MAP.get(road.road_id)
    if not feeders:
        return None
    dist = road.stop_x - car.x
    if dist < 0.5 or dist > YIELD_LOOK:
        return None

    to_junction, speeds = [], []
    for feedID, off in feeders:
        up = ActiveRoadsList[feedID]
        for lane in up.cars_data:
            for carOB in lane:
                nextID = carOB.next_road_id
                if nextID is not None and ActiveRoadsList[nextID].is_ring:
                    to_junction.append(up.lenght - carOB.x + off)
                    speeds.append(carOB.v)

    if to_junction:
        gap_t = np.array(to_junction) / np.maximum(speeds, V_MIN) - dist / max(car.v, V_MIN)
        patience = max(0.3, 1.0 - car.yield_wait / 20.0)
        if ((gap_t > -T_FOLLOW) & (gap_t < T_CRIT * patience)).any():
            if car.v < 0.5:
                car.yield_wait += DT
            return dist, 0.0
    car.yield_wait = 0.0
    return None

def approach_limit(car, road):
    #speed form which car can still slow down comfortably
    limit = road.speed_limit
    nextID = car.next_road_id
    if nextID is None:
        return limit
    nxt = ActiveRoadsList[nextID].speed_limit
    if nxt >= limit:
        return limit
    d = max(0.0, road.stop_x - car.x)
    return min(limit, 3.6 * math.sqrt((nxt / 3.6) ** 2 + 2 * car.profile.b * d))

def box_leader(car, road, t):
    #stop at the stop line if there is o room the next road
    if road.is_ring:
        return None
    NextID = car.next_road_id
    if NextID is None:
        return None
    distance = road.stop_x - car.x
    if distance < 0.5 or distance > BOX_LOOK:   #already past or still far
        return None

    nextRoad = ActiveRoadsList[NextID]
    queue = nextRoad.cars_data[entry_lane(car.next_turn, car.lane, int(nextRoad.lanes))]
    free = (queue[-1].x - queue[-1].length) if queue else float('inf')
    if free >= car.length + BOX_MARGIN:
        car.box_wait = 0.0
        return None
    if car.v < 0.5:
        car.box_wait += DT
        if car.box_wait > BOX_PATIENCE:
            return None
    return distance, 0.0

def cars_stuck_in_junction():
    # cars stopped btw stopline and end of road, use the box blocking
    n = 0
    for car in ActiveCarsNow:
        road = ActiveRoadsList[car.road_id]
        if car.v < 0.5 and road.stop_x < car.x < road.lenght:
            n += 1
    return n

    
def carriageway_width_m(lanes):
    return lanes * LANE_WIDTH + (lanes - 1) * DASHES_WIDTH

def carriageway_shift_m(road):
    if road.oneway:
        return 0.0
    return DRIVE_SIDE * carriageway_width_m(road.lanes)/2

def lane_center_offset_m(road, lane):
    width  = carriageway_width_m(road.lanes)
    return (lane * (LANE_WIDTH + DASHES_WIDTH) + LANE_WIDTH/2 - width / 2 + carriageway_shift_m(road))

def spawner(router, ActiveRoadsList, AvailableLocations):
    NoOfLocations = len(AvailableLocations) - 1
    spawnIndex = random.randint(1,NoOfLocations)
    destinationIndex = random.randint(1,NoOfLocations)
    while spawnIndex == destinationIndex:
        destinationIndex = random.randint(1,NoOfLocations)

    spawn = AvailableLocations[spawnIndex]
    destination = AvailableLocations[destinationIndex]

    Xpos = random.randint(1,round(ActiveRoadsList[spawn].lenght))
    lane = random.choice([0 , ActiveRoadsList[spawn].lanes - 1])
    if not lane_is_clear(ActiveCarsNow, spawn, lane, Xpos):
        return

    destinationData = [ActiveRoadsList[destination].EndNode,destination, random.randint(6,round(ActiveRoadsList[destination].lenght))]

    spawn_car(
            router=router,
            cars=ActiveCarsNow,
            car_id=str(uuid.uuid4()),
            road_id=spawn,
            x=Xpos,
            lane=lane,
            speed_kmh=30,
            dest_road=destinationData[1],
            dest_x=destinationData[2],
            length=4.5,
            rng= random.Random()
            )

def spawn_car(router, cars, car_id, road_id, x, lane, speed_kmh,
                dest_road, dest_x, length, rng):
    pref = rng.randint(0, 1)
    route = router.route(road_id, dest_road, pref)
    if route is None:
        return None
    car = Car(car_id, length, route, rng=rng, lane=lane, start_x=x,
                start_speed_kmh=speed_kmh, dest_road=dest_road, dest_x=dest_x)
    cars.append(car)
    return car

def turn_urgency(car, road):
    #gives a score form 0.0 to 1.0, whowing how urgenty a car needs to merge into a turn lane
    if car.next_turn not in ('left', 'right'):
        return 0.0

    stop_line = getattr(road, 'stop_x', road.lenght)

    distance_to_turn = stop_line - car.x

    if distance_to_turn < 0.0:
        distance_to_turn = 0.0

    if distance_to_turn >= TURN_ZONE:
        return 0.0

    urgency = 1.0 - (distance_to_turn / TURN_ZONE)
    #as car gets closer inside TURN_ZONE, urgency rises
    return urgency





