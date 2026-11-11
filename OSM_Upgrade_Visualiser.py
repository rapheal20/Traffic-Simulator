
import pygame
import math
from collections import Counter
import osmnx as ox
import statistics as st
import numpy as np
import uuid
import sys
import random
import re

from RealMapsLoader import screen_nodes, projectedGraph, scale, FinalLaneCounts
from Simulation import DEFAULT_LIMITS
from Object_Classes.roads import roads
from Object_Classes.nodes import nodes
# from Object_Classes.car import car
from Active_Lists.ActiveList import ActiveNodesDict, NodesforRoad, ActiveRoadsList, ActiveCarsNow
from Object_Classes.IDM_Car import Car
from Object_Classes.Router import Router
# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.15 #in meters
DASH_length = 3
GAP_length = 3

#LANE CHANGING CONST.
LANE_SAFE_BRAKE = 4.0   #max braking to impose on new follower
LANE_GAIN = 0.3     #minimum benefit to change lane
LANE_COOLDOWN = 5.0


#SCREEN CONSTANTS
SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1366
BG_COLOR = (227, 227, 227)     # Dark gray background
GRID_COLOR = (182, 182, 182)    #light gray
CELL_SIZE = 50

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
elapsed = 0

# PANNING
camera_X = 0
camera_Y = 0
is_dragging = False
last_mouse_pos = (0,0)  
#camera_X and camera_Y are the anchors of the screen
#they are used to find out how far adn where the screen is dragged
#last_mouse_pos keeps the last postion of the mouse to calculaet the change  

#ZOOM
zoom_scale = 1.0
MIN_ZOOM = 0.2
MAX_ZOOM = 5.0

carWidth = 2
carlength = 4.5

running = True
mapSaved = False

AvailableLocations = []
# MAP SAVING
for u, v, data in projectedGraph.edges(data=True):
    # Make sure both ends of the road exist in our screen dictionary
    if u in screen_nodes and v in screen_nodes:
        name = data.get('name')
        if isinstance(name,list):
            name = name[0]
        LaneNo = FinalLaneCounts.get(name)
        #Linear Algebra concept
        start_pos = screen_nodes[u][0]
        end_pos = screen_nodes[v][0]
        
        
        def findSpeedLimit(data):
            speedlimit = data.get('maxspeed', None)
            if isinstance(speedlimit, list):
                speedlimit = speedlimit[0]
            
            if speedlimit:
                if speedlimit.endswith("mph"):
                    speed = re.search(r"\d+", speedlimit)
                    speedLimit_KMH = round(float(speed.group(0)) * 1.6)
            else:
                roadtype = data.get('highway')
                if isinstance(roadtype, list):
                    roadtype = roadtype[0]
                speedLimit_KMH = DEFAULT_LIMITS.get(roadtype, 40)

            return speedLimit_KMH


        Speed_Limit_KMH = findSpeedLimit(data)
        # print(speedLimit_KMH)
        # sys.exit()

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

        oneway = data.get('oneway', True)
        if not oneway:
            if LaneNo % 2 != 0:
                LaneNo += 1

        uniqueID = str(uuid.uuid4())

        if u not in NodesforRoad:
            NodesforRoad[u] = []
        NodesforRoad[u].append(uniqueID)
        if v not in NodesforRoad:
            NodesforRoad[v] = []
        NodesforRoad[v].append(uniqueID)


        #if the road has a single lane it is considered minor and will be used for spawing cars
        if LaneNo < 2:
            AvailableLocations.append(uniqueID)
            
        roads(
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

for nodeID, nodeData in projectedGraph.nodes(data=True):
    # print(nodeID, nodeData)
    if nodeID in screen_nodes:
        coordinates = screen_nodes[nodeID][0]
        roadNum = screen_nodes[nodeID][1]
        nodeType = nodeData.get('highway', None)
        connectedroads = NodesforRoad[nodeID]
        maxLanes = 0
        
        for roadID in connectedroads:
            laneNo = (int(ActiveRoadsList[roadID].lanes))
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

router = Router(ActiveRoadsList)


def spawn_car(cars, car_id, road_id, x, lane, speed_kmh,
                dest_road, dest_x, length, rng):
    pref = rng.randint(0, 1)
    route = router.route(road_id, dest_road, pref)
    if route is None:
        return None
    car = Car(car_id, length, route, rng=rng, lane=lane, start_x=x,
                start_speed_kmh=speed_kmh, dest_road=dest_road, dest_x=dest_x)
    cars.append(car)
    return car
    
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

    if i > 0:
        gap = gap_between(car, current_lane[i-1])
        leader_v = current_lane[i-1].v
    else:
        gap, leader_v = None, 0.0

    a_now = car.compute_acceleration(limit, gap, leader_v)

    best_target = None
    best_score = LANE_GAIN
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
                a_follower_before = follower.compute_acceleration(limit, gap_between(follower, leader), leader_v)
            else:
                a_follower_before = follower.compute_acceleration(limit)
            a_follower_after = follower.compute_acceleration(limit, gap_follower, car.v)
            if a_follower_after < -LANE_SAFE_BRAKE:
                continue
            loss = max(0.0, a_follower_before - a_follower_after)
        score = (a_new - a_now) - car.politeness * loss
        if score > best_score:
            best_target, best_score = target, score

    if best_target is not None:
        current_lane.remove(car)
        target_lane = lanes[best_target]
        index = sum(1 for o in target_lane if o.x > car.x)
        target_lane.insert(index, car)
        car.lane = best_target
        car.lane_cooldown = LANE_COOLDOWN









# sys.exit()
accumulator = 0.0
SIM_SPEED = 5.0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #for left mouse button
                is_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:
                #if the mouse is  dragging it finds he following
                # change in x
                # change in y
                # then it add them into the camera postion
                #then changes the last_mouse_pos to new mosue, this remvoes the jerk by changing for each move
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_X += dx
                camera_Y += dy
                last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            #in an mousewheel action, event.y tells how far and in what direction has he mosue been moved
            mouse_X, mouse_Y = pygame.mouse.get_pos()

            old_World_X = (mouse_X - camera_X)/zoom_scale 
            old_World_Y = (mouse_Y - camera_Y)/zoom_scale 

            zoom_scale += event.y * 0.05
            scale = zoom_scale

            if scale > MAX_ZOOM:
                scale = MAX_ZOOM
            elif scale < MIN_ZOOM:
                scale = MIN_ZOOM 

            new_world_X = (mouse_X - camera_X) / zoom_scale
            new_world_Y = (mouse_Y - camera_Y) / zoom_scale      

            camera_X += (new_world_X - old_World_X) * zoom_scale
            camera_Y += (new_world_Y - old_World_Y) * zoom_scale

            #mouse_X is the pixel coordinate of our monitor or screen
            #camera_X is the offset
            #the subtraction is for the pan and then division factors in the zoom

    #Initializing cars
    while len(ActiveCarsNow) != 100:
        NoOfLocations = len(AvailableLocations) - 1
        spawnIndex = random.randint(1,NoOfLocations)
        destinationIndex = random.randint(1,NoOfLocations)
        while spawnIndex == destinationIndex:
            destinationIndex = random.randint(1,NoOfLocations)

        spawn = AvailableLocations[spawnIndex]
        destination = AvailableLocations[destinationIndex]

        Xpos = random.randint(1,round(ActiveRoadsList[spawn].lenght))
        destinationData = [ActiveRoadsList[destination].EndNode,destination, random.randint(6,round(ActiveRoadsList[destination].lenght))]

        spawn_car(cars=ActiveCarsNow,
                car_id=str(uuid.uuid4()),
                road_id=spawn,
                x=Xpos,
                lane=0,
                speed_kmh=30,
                dest_road=destinationData[1],
                dest_x=destinationData[2],
                length=4.5,
                rng= random.Random()
                )



    def simulation_step(cars, dt):
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
                    decisions.append((carOBJ, carOBJ.compute_acceleration(road.speed_limit, gap, leader_v)))

        for car, a in decisions:
            car.apply(a, dt)
            car.update_route(ActiveRoadsList)

        cars[:] = [c for c in cars if not c.finished] #removes any cars that is finished

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
        next_Lane = min(car.lane, int(next_Road.lanes) - 1)
        cars_There = next_Road.cars_data[next_Lane]
        if not cars_There:
            return None, 0.0

        lead = cars_There[-1]
        gap = (road.lenght - car.x) + (lead.x - lead.length)
        return gap, lead.v

    DT = 0.1
    frame_time = clock.tick(60) / 1000.0
    accumulator += min(frame_time, 0.25) * SIM_SPEED
    while accumulator >= DT:
        simulation_step(ActiveCarsNow, DT)
        accumulator -= DT

    def drawGrid():
        current_Cell_Size = CELL_SIZE * zoom_scale

        start_X = camera_X % current_Cell_Size
        start_Y = camera_Y % current_Cell_Size
        #here if the CELL_SIZE is 40, adn we drga camera to an offset of 42,42
        # it finds outthe moda dn starts the grid at 2

        screen.fill(BG_COLOR)
        for x in range(int(start_X), SCREEN_WIDTH, int(current_Cell_Size)):
            pygame.draw.line(screen, GRID_COLOR, (x,0), (x,SCREEN_HEIGHT))

        for y in range(int(start_Y), SCREEN_HEIGHT, int(current_Cell_Size)):
            pygame.draw.line(screen, GRID_COLOR, (0,y), (SCREEN_WIDTH,y))
    cameraOffset = np.array([camera_X, camera_Y], dtype=float)

    drawGrid()

    for roadID, roadData in ActiveRoadsList.items():
        LaneNo = roadData.lanes
        vector1 = roadData.coordinates[0]
        vector2 = roadData.coordinates[1]

        screen1 = (vector1 * scale) + cameraOffset
        screen2 = (vector2 * scale) + cameraOffset

        length = roadData.lenght

        dashPixelWidth = max(1, int(DASHES_WIDTH * scale)) #if dashes width less then 1 then default width 1px
        
        # skips very small road segments/ removes garbage values
        if length >= 10: 
            Unit_Dir = roadData.UnitVector #creates the unit vector
            normal = roadData.NormalVector
            # we need the normal as to draw out the thickness of our roads we need the exact perpendicualr of its direction
            # does the dot multiplication rotates it by 90 degree

            roadWidth = (LaneNo * LANE_WIDTH * scale) + ((LaneNo - 1) * dashPixelWidth)
            # nodeBuffer = bufferArea * scale
            halfWidth = roadWidth/2


            nodeBufferPX1 = (ActiveNodesDict[roadData.StartNode].MaxLanes * LANE_WIDTH * scale)/2 
            nodeBufferPX2 = (ActiveNodesDict[roadData.EndNode].MaxLanes * LANE_WIDTH * scale)/2 
            #get the node obj from the road list and find its maxlanes and cuts the road only that much

            #multiplying the UnitVector gives us a new arrow with that length
            trimmedP1 = screen1 + Unit_Dir * nodeBufferPX1
            trimmedP2 = screen2 - Unit_Dir * nodeBufferPX2
            trimmedlength = np.linalg.norm(trimmedP2-trimmedP1)

            # normal is also a unit vector but in perpendicualr direction
            Corner1 = trimmedP1 + normal * halfWidth
            Corner2 = trimmedP2 + normal * halfWidth
            Corner3 = trimmedP2 - normal * halfWidth
            Corner4 = trimmedP1 - normal * halfWidth

            PolygonCords = [tuple(Corner1), tuple(Corner2), tuple(Corner3), tuple(Corner4)]

            # if roadData.oneway:
            #     pygame.draw.polygon(surface=screen, color=(0, 0, 255), points=PolygonCords)
            # else:
            #     pygame.draw.polygon(surface=screen, color=(255, 0, 0), points=PolygonCords)
            # pygame.draw.polygon(surface=screen, color=colouring[roadData.osmid], points=PolygonCords)
            pygame.draw.polygon(surface=screen, color=(25,25,25), points=PolygonCords)

            dashlength = DASH_length * scale
            dashGap = GAP_length * scale
        
            cycleLen = dashlength + dashGap
            dashesNo = int(trimmedlength//cycleLen)
            if dashesNo > 0:
                totalDashedDist = (dashlength*dashesNo) + (dashGap*(dashesNo-1))
                startGap = (trimmedlength - totalDashedDist)/2
            else:
                totalDashedDist = 0
                startGap = 0


            roadWidth_M = (LaneNo * LANE_WIDTH) + ((LaneNo - 1) * DASHES_WIDTH)
            halfroadWidth_M = roadWidth_M/2
            

            for i in range(1, LaneNo):
                offset = ((i * LANE_WIDTH) + ((i-1) * DASHES_WIDTH)) - halfroadWidth_M
                pixel_offset = offset * scale

                line_Vector1 = trimmedP1 + normal * pixel_offset #gets on the right width of the road
                current_pos = line_Vector1 + Unit_Dir * startGap # gets on the right length of the road
                for j in range(dashesNo):
                    dashEnd = current_pos + Unit_Dir * dashlength
                    pygame.draw.line(screen,(255,255,255), tuple(current_pos), tuple(dashEnd), width=dashPixelWidth)
                    current_pos += Unit_Dir * cycleLen

    for nodeID, nodeData in ActiveNodesDict.items():
        nodeType = nodeData.Type
        if nodeType == 'traffic_signals':         
            nodePos = np.array(nodeData.Coordinates, dtype=float)
            screenPos = (nodePos * scale) + cameraOffset
            halfnodeDim_M = (nodeData.MaxLanes * LANE_WIDTH + (nodeData.MaxLanes-1) * DASHES_WIDTH)/2
            halfnodeDim_PX = halfnodeDim_M * scale

            normal = ActiveRoadsList[nodeData.MainRoad].NormalVector
            tangent = ActiveRoadsList[nodeData.MainRoad].UnitVector

            NCorner1 = screenPos + (tangent * halfnodeDim_PX) + (normal * halfnodeDim_PX)
            NCorner2 = screenPos + (tangent * halfnodeDim_PX) - (normal * halfnodeDim_PX)
            NCorner3 = screenPos - (tangent * halfnodeDim_PX) - (normal * halfnodeDim_PX)
            NCorner4 = screenPos - (tangent * halfnodeDim_PX) + (normal * halfnodeDim_PX)

            NodeCoordinates = (NCorner1, NCorner2, NCorner3, NCorner4)

            pygame.draw.polygon(screen, (25,25,25), points=NodeCoordinates)

    #     elif nodeType == 'roundabout':

    #     else:

    # print(ActiveCarsNow)
    

    for carObj in ActiveCarsNow:
        carRoad = carObj.road_id
        if not carRoad or carRoad not in ActiveRoadsList:
            continue

        roadData = ActiveRoadsList[carRoad]
        p1World = (roadData.coordinates)[0]

        unitVector = roadData.UnitVector
        normal = roadData.NormalVector

        #finds distance travelled across the road
        carWorldPos = p1World + (unitVector * carObj.x)

        LaneNo = roadData.lanes
        LaneOffset = (carObj.lane - (LaneNo - 1)/2.0) * LANE_WIDTH
        CarCenterWorld = carWorldPos + (normal * LaneOffset)


        CarLen_PX = carObj.length
        halfCarWidthPX = (carWidth)/2.0

        #calculate coordinates, by using the unitVector car len, and normalVector car width
        c1_world = (CarCenterWorld + (normal * halfCarWidthPX))
        c2_world = (CarCenterWorld - (normal * halfCarWidthPX))
        c3_world = (CarCenterWorld - (unitVector * CarLen_PX) - (normal * halfCarWidthPX))
        c4_world = (CarCenterWorld - (unitVector * CarLen_PX) + (normal * halfCarWidthPX))

        screenCorners = [
            tuple((c1_world * scale) + cameraOffset),
            tuple((c2_world * scale) + cameraOffset),
            tuple((c3_world * scale) + cameraOffset),
            tuple((c4_world * scale) + cameraOffset)
        ]
        
        

        pygame.draw.polygon(surface=screen, color=(255,0,0), points=screenCorners)

    #updates the display
    pygame.display.flip()



pygame.quit()


