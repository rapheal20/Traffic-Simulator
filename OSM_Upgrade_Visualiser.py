
import pygame
import math
from collections import Counter
import osmnx as ox
import statistics as st
import numpy as np

pygame.init()

screen = pygame.display.set_mode((1366,1000))
from RealMapsLoader import screen_nodes, projectedGraph, scale, FinalLaneCounts
# Conversion: 1m = 5px


# from Object_Classes.car import road1, road2, car1
import ObjectCreations
from Active_Lists.ActiveRoads import ActiveRoadsList
from Active_Lists.ActiveCars import ActiveCarsNow
# Roadpx = (500 * 5, )

# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.15 #in meters
DASH_LENGHT = 3
GAP_LENGHT = 3
# scale = 5

carWidth = 1.8
carLenght = 4.5


running = True
# clock = pygame.time.Clock()
elapsed = 0
while running:


    #pygame.event.get() returns all the events happening
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    # dt = clock.tick(60) / 1000


    # makes the screen white
    screen.fill((25,25,25))

    # Loop through every edge (road) in the graph
    for u, v, data in projectedGraph.edges(data=True):
        # Make sure both ends of the road exist in our screen dictionary
        # print(u, v)
        # print(data)
        if u in screen_nodes and v in screen_nodes:
            osmid = data.get('osmid')
            if isinstance(osmid,list):
                osmid = osmid[0]
            LaneNo = FinalLaneCounts.get(osmid,1)


            #Linear Algebra concept
            start_pos = screen_nodes[u][0]
            end_pos = screen_nodes[v][0]

            #np.array converts it into vector
            vector1 = np.array(start_pos, dtype=float)
            vector2 = np.array(end_pos, dtype=float)

            #vector subtraction so each element is subtracted from its corresponding element
            direction = vector2 - vector1

            # calculates its euclidean lenght, basically the hypotneous of it
            lenght = np.linalg.norm(direction)
            dashPixelWidth = max(1, int(DASHES_WIDTH * scale)) #if dashes width less then 1 then default width 1px
            
            # skips very small road segments/ removes garbage values
            if lenght >= 10: 
                Unit_Dir = direction/lenght #creates the unit vector
                rotation_Matrix = np.array([[0,-1],[1,0]]) #2D vector whcih roates any value by 90 degrees counterclockwise
                normal = rotation_Matrix.dot(Unit_Dir) #does dot multiplication
                # we need the normal as to draw out the thickness of our roads we need the exact perpendicualr of its direction
                # does the dot multiplication rotates it by 90 degree

                roadWidth = (LaneNo * LANE_WIDTH * scale) + ((LaneNo - 1) * dashPixelWidth)
                # nodeBuffer = bufferArea * scale
                halfWidth = roadWidth/2

                #multiplying the UnitVector gives us a new arrow with that lenght
                trimmedP1 = vector1 + Unit_Dir * roadWidth
                trimmedP2 = vector2 - Unit_Dir * roadWidth
                trimmedLenght = np.linalg.norm(trimmedP2-trimmedP1)

                # normal is also a unit vector but in perpendicualr direction
                Corner1 = trimmedP1 + normal * halfWidth
                Corner2 = trimmedP2 + normal * halfWidth
                Corner3 = trimmedP2 - normal * halfWidth
                Corner4 = trimmedP1 - normal * halfWidth


                PolygonCords = [tuple(Corner1), tuple(Corner2), tuple(Corner3), tuple(Corner4)]

                pygame.draw.polygon(surface=screen, color=(60, 60, 60), points=PolygonCords)



                dashLenght = DASH_LENGHT * SCALE_PER_M
                dashGap = GAP_LENGHT * SCALE_PER_M
            
                cycleLen = dashLenght + dashGap
                dashesNo = int(trimmedLenght//cycleLen)
                if dashesNo > 0:
                    totalDashedDist = (dashLenght*dashesNo) + (dashGap*(dashesNo-1))
                    startGap = (trimmedLenght - totalDashedDist)/2
                else:
                    totalDashedDist = 0
                    startGap = 0


                roadWidth_M = (LaneNo * LANE_WIDTH) + ((LaneNo - 1) * DASHES_WIDTH)
                halfroadWidth_M = roadWidth_M/2
                

                for i in range(1, LaneNo):
                    offset = ((i * LANE_WIDTH) + ((i-1) * DASHES_WIDTH)) - halfroadWidth_M
                    pixel_offset = offset * scale

                    line_Vector1 = trimmedP1 + normal * pixel_offset #gets on the right width of the road
                    current_pos = trimmedP1 + Unit_Dir * startGap # gets on the right lenght of the road
                    for j in range(dashesNo):
                        dashEnd = current_pos + Unit_Dir * dashLenght
                        pygame.draw.line(screen,(255,255,255), tuple(current_pos), tuple(dashEnd), width=dashPixelWidth)
                        current_pos += Unit_Dir * cycleLen






                # start_pos = (int(screen_nodes[u][0][0]-bufferArea), int(screen_nodes[u][0][1]-bufferArea))
                # end_pos = (int(screen_nodes[v][0][0]-bufferArea), int(screen_nodes[v][0][1]-bufferArea))
                # width = int(LaneNo * LANE_WIDTH)


            # roadX = roadObj.cordinates[0] * SCALE_PER_M
            # roadY = roadObj.cordinates[1] * SCALE_PER_M
            # roadLenght = roadObj.lenght * SCALE_PER_M
            # roadWidth = roadObj.lanes * LANE_WIDTH * SCALE_PER_M + (roadObj.lanes - 1) * DASHES_WIDTH
            # roadSize = (roadX, roadY, roadLenght, roadWidth)
            # pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)


            
            # Draw the road line (gray color, 2 pixels wide)
            # pygame.draw.line(screen, (100, 100, 100), start_pos, end_pos, width)










    # for roadObj in ActiveRoadsList.values():
    #     if roadObj.orientation == 0:
    #         roadX = roadObj.cordinates[0] * SCALE_PER_M
    #         roadY = roadObj.cordinates[1] * SCALE_PER_M
    #         roadLenght = roadObj.lenght * SCALE_PER_M
    #         roadWidth = roadObj.lanes * LANE_WIDTH * SCALE_PER_M + (roadObj.lanes - 1) * DASHES_WIDTH
    #         roadSize = (roadX, roadY, roadLenght, roadWidth)
    #         pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

    #         #road dashes
    #         dashLenght = 3 * SCALE_PER_M
    #         dashGap = 6 * SCALE_PER_M
    #         DashesNo = int(roadLenght) // (dashLenght+dashGap)
    #         DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
    #         StartGap = (roadLenght-DashedDist)//2
    #         dashStart = roadX + StartGap
    #         for j in range(1, roadObj.lanes): 
    #             dashY = roadY + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
    #             DashesNo = int(roadLenght) // (dashLenght+dashGap)
    #             dashStartPos = dashStart
    #             for i in range(0,DashesNo):
    #                 pygame.draw.line(screen,(255,255,255), (dashStartPos, dashY), (dashStartPos+dashLenght, dashY), DASHES_WIDTH)
    #                 dashStartPos += (dashLenght+dashGap)


    #     elif roadObj.orientation == 1:
    #         roadX = roadObj.cordinates[0] * SCALE_PER_M
    #         roadY = roadObj.cordinates[1] * SCALE_PER_M
    #         roadLenght = roadObj.lenght * SCALE_PER_M 
    #         roadWidth = (roadObj.lanes * LANE_WIDTH * SCALE_PER_M) + (roadObj.lanes - 1) * DASHES_WIDTH
    #         roadSize = (roadX, roadY, roadWidth, roadLenght)
    #         pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

    #         dashLenght = 3 * SCALE_PER_M
    #         dashGap = 6 * SCALE_PER_M
    #         DashesNo = int(roadLenght) // (dashLenght+dashGap)
    #         DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
    #         StartGap = (roadLenght-DashedDist)//2
    #         dashStart = roadY + StartGap
    #         for j in range(1, roadObj.lanes): 
    #             dashX = roadX + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
    #             DashesNo = int(roadLenght) // (dashLenght+dashGap)
    #             dashStartPos = dashStart
    #             for i in range(0,DashesNo):
    #                 pygame.draw.line(screen,(255,255,255), (dashX, dashStartPos), (dashX, dashStartPos+dashLenght), DASHES_WIDTH)
    #                 dashStartPos += (dashLenght+dashGap)

                    
    #updates the display
    pygame.display.flip()


pygame.quit()


#     (i.carAccelerate())
