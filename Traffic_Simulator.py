import pygame
import numpy as np
import uuid
import sys
import random


# from RealMapsLoader import screen_nodes, projectedGraph, scale, FinalLaneCounts
from Simulation_Helpers import *
from Active_Lists.ActiveList import ActiveNodesDict, NodesforRoad, ActiveRoadsList, ActiveCarsNow
from Object_Classes.Router import Router
from Object_Classes.TrafficLights import ActiveSignals, build_signals
from Object_Classes.turn import build_turn_table, TURN_TABLE

#SCREEN CONSTANTS
SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1366
BG_COLOR = (227, 227, 227)     # Dark gray background
GRID_COLOR = (182, 182, 182)    #light gray
CELL_SIZE = 50

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()

# PANNING
camera_X = 0    #anchors of the screen
camera_Y = 0
is_dragging = False
last_mouse_pos = (0,0)      #last postion of the mouse to calculaet the change  

#ZOOM
zoom_scale = 1.0
MIN_ZOOM = 0.2
MAX_ZOOM = 5.0

running = True
mapSaved = False

coordinates, radius = (40.7580, -73.9855), 400
scale, AvailableLocations = Initialize_Map(coordinates, radius, ActiveNodesDict, NodesforRoad)
router = Router(ActiveRoadsList)
build_turn_table(ActiveRoadsList)
print(len(TURN_TABLE))

# sys.exit()
sim_time = 0.0
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
        spawner(router, ActiveRoadsList, AvailableLocations)

    frame_time = clock.tick(60) / 1000.0
    accumulator += min(frame_time, 0.25) * SIM_SPEED
    while accumulator >= DT:
        simulation_step(ActiveCarsNow, DT, sim_time)
        sim_time += DT
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

            shift_px = carriageway_shift_m(roadData) * scale
            screen1 = screen1 + normal * shift_px
            screen2 = screen2 + normal * shift_px

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

            pygame.draw.polygon(surface=screen, color=(25,25,25), points=PolygonCords)

            if not roadData.oneway:
                c1 = trimmedP1 - normal * shift_px
                c2 = trimmedP2 - normal * shift_px
                pygame.draw.line(screen, (230,200,40), tuple(c1), tuple(c2))

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
    
    LIGHT_COL = {'green' : (0,200,0), "yellow" : (240, 190, 0), 'red':(220,0,0)}

    for roadID, roadData in ActiveRoadsList.items():
        light = ActiveSignals.get(roadData.EndNode)
        if light is None or roadData.lenght < 10:
            continue
        unitVec = roadData.UnitVector
        normal = roadData.NormalVector
        endCord = roadData.coordinates[1]
        buffer = ActiveNodesDict[roadData.EndNode].MaxLanes * LANE_WIDTH / 2
        half = carriageway_width_m(roadData.lanes) / 2
        centre = endCord - unitVec * buffer + normal * carriageway_shift_m(roadData)
        a = (centre + normal * half) * scale + cameraOffset
        b = (centre - normal * half) * scale + cameraOffset
        pygame.draw.line(screen, LIGHT_COL[light.state(roadID, sim_time)], tuple(a), tuple(b), max(2, int(2 * scale)))



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
        # LaneOffset = (carObj.lane - (LaneNo - 1)/2.0) * LANE_WIDTH
        LaneOffset = lane_center_offset_m(roadData, carObj.lane)
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


        TURN_COL = {'left': (255, 150, 0), 'right': (170, 60, 200),
            'straight': (40, 120, 220), None: (130, 130, 130)}
        colour = TURN_COL[carObj.next_turn]
        # (255,0,0)
        pygame.draw.polygon(surface=screen, color=colour, points=screenCorners)

    #updates the display
    pygame.display.flip()



pygame.quit()


