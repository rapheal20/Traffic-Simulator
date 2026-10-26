
import pygame
import math
from collections import Counter
import osmnx as ox
import statistics as st
import numpy as np
import uuid
import sys

pygame.init()

from RealMapsLoader import screen_nodes, projectedGraph, scale, FinalLaneCounts
# Conversion: 1m = 5px


from Object_Classes.roads import roads
from Object_Classes.nodes import nodes
# import ObjectCreations

from Active_Lists.ActiveNodes import ActiveNodesDict, NodesforRoad
from Active_Lists.ActiveRoads import ActiveRoadsList
from Active_Lists.ActiveCars import ActiveCarsNow
# Roadpx = (500 * 5, )

# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.15 #in meters
DASH_length = 3
GAP_length = 3
# VScale = scale

#SCREEN CONSTANTS
SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1366
BG_COLOR = (227, 227, 227)     # Dark gray background
GRID_COLOR = (182, 182, 182)    #light gray
CELL_SIZE = 50
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

carWidth = 1.8
carlength = 4.5

running = True
mapSaved = False

# MAP SAVING
for u, v, data in projectedGraph.edges(data=True):

    # Make sure both ends of the road exist in our screen dictionary
    if u in screen_nodes and v in screen_nodes:
        osmid = data.get('osmid')
        if isinstance(osmid,list):
            osmid = osmid[0]
        LaneNo = FinalLaneCounts.get(osmid,1)

        #Linear Algebra concept
        start_pos = screen_nodes[u][0]
        end_pos = screen_nodes[v][0]

        speedlimit = data.get('maxspeed', False)

        #np.array converts it into vector
        vector1 = np.array(start_pos, dtype=float)
        vector2 = np.array(end_pos, dtype=float)

        #vector subtraction so each element is subtracted from its corresponding element
        direction = vector2 - vector1

        # calculates its euclidean length, basically the hypotneous of it
        length = round(np.linalg.norm(direction),0)
        UnitVector = direction/length
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
        


        roads(
            roadID= uniqueID,
            coordinates= [vector1,vector2],
            roadLength= length,
            lanes= LaneNo,
            oneway= oneway,
            speedLimit= speedlimit,
            unitVec= UnitVector
        )


print(NodesforRoad)

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


# print(ActiveNodesDict)

# sys.exit()

# print(ActiveRoadsList)


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

            # print(scale)

            new_world_X = (mouse_X - camera_X) / zoom_scale
            new_world_Y = (mouse_Y - camera_Y) / zoom_scale      

            camera_X += (new_world_X - old_World_X) * zoom_scale
            camera_Y += (new_world_Y - old_World_Y) * zoom_scale

            #mouse_X is the pixel coordinate of our monitor or screen
            #camera_X is the offset
            #the subtraction is for the pan and then division factors in the zoom

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
        if length >= 20: 
            Unit_Dir = roadData.UnitVector #creates the unit vector
            rotation_Matrix = np.array([[0,-1],[1,0]]) #2D vector whcih roates any value by 90 degrees counterclockwise
            normal = rotation_Matrix.dot(Unit_Dir) #does dot multiplication
            # we need the normal as to draw out the thickness of our roads we need the exact perpendicualr of its direction
            # does the dot multiplication rotates it by 90 degree

            roadWidth = (LaneNo * LANE_WIDTH * scale) + ((LaneNo - 1) * dashPixelWidth)
            # nodeBuffer = bufferArea * scale
            halfWidth = roadWidth/2

            #multiplying the UnitVector gives us a new arrow with that length
            trimmedP1 = screen1 + Unit_Dir * roadWidth
            trimmedP2 = screen2 - Unit_Dir * roadWidth
            trimmedlength = np.linalg.norm(trimmedP2-trimmedP1)

            # normal is also a unit vector but in perpendicualr direction
            Corner1 = trimmedP1 + normal * halfWidth
            Corner2 = trimmedP2 + normal * halfWidth
            Corner3 = trimmedP2 - normal * halfWidth
            Corner4 = trimmedP1 - normal * halfWidth

            PolygonCords = [tuple(Corner1), tuple(Corner2), tuple(Corner3), tuple(Corner4)]

            if roadData.oneway:
                pygame.draw.polygon(surface=screen, color=(0, 0, 255), points=PolygonCords)
            else:
                pygame.draw.polygon(surface=screen, color=(255, 0, 0), points=PolygonCords)
            # pygame.draw.polygon(surface=screen, color=(60, 60, 60), points=PolygonCords)

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


            UnitVector_R = ActiveRoadsList[nodeData.MainRoad].UnitVector
            normal = rotation_Matrix.dot(UnitVector_R)
            tangent = UnitVector_R

            NCorner1 = screenPos + (tangent * halfnodeDim_PX) + (normal * halfnodeDim_PX)
            NCorner2 = screenPos + (tangent * halfnodeDim_PX) - (normal * halfnodeDim_PX)
            NCorner3 = screenPos - (tangent * halfnodeDim_PX) - (normal * halfnodeDim_PX)
            NCorner4 = screenPos - (tangent * halfnodeDim_PX) + (normal * halfnodeDim_PX)

            NodeCoordinates = (NCorner1, NCorner2, NCorner3, NCorner4)

            pygame.draw.polygon(screen, (0,255,0), points=NodeCoordinates)

    #     elif nodeType == 'roundabout':

    #     else:


    

    # for carObj in ActiveCarsNow:
    #     carRoad = ActiveRoadsList[carObj.current_road]

    #updates the display
    pygame.display.flip()


pygame.quit()


