import pygame

pygame.init()

screen = pygame.display.set_mode((1366,1000))

# Conversion: 1m = 5px


# from Object_Classes.car import road1, road2, car1
import ObjectCreations
from Active_Lists.ActiveRoads import ActiveRoadsList
from Active_Lists.ActiveCars import ActiveCarsNow
# Roadpx = (500 * 5, )

# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 2 #in px


carWidth = 1.8
carLenght = 4.5


# road1 = roads(
#                 roadID= 'AA01',
#                 roadLength = 500,
#                 lanes = 3,
#                 orientation=0,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [0, 250, 500],
#                 trafficLight = 500,
#                 )

# road2 = roads(
#                 roadID= 'BB01',
#                 roadLength = 500,
#                 lanes = 2,
#                 orientation=1,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [0, 250, 500],
#                 trafficLight = 500,
#                 )


running = True
while running:


    #pygame.event.get() returns all the events happening
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # makes the screen white
    screen.fill((25,25,25))
    for roadObj in ActiveRoadsList.values():
        if roadObj.orientation == 0:
            roadX = roadObj.cordinates[0] * SCALE_PER_M
            roadY = roadObj.cordinates[1] * SCALE_PER_M
            roadLenght = roadObj.lenght * SCALE_PER_M
            roadWidth = roadObj.lanes * LANE_WIDTH * SCALE_PER_M + (roadObj.lanes - 1) * DASHES_WIDTH
            roadSize = (roadX, roadY, roadLenght, roadWidth)
            pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

            #road dashes
            dashLenght = 3 * SCALE_PER_M
            dashGap = 6 * SCALE_PER_M
            DashesNo = int(roadLenght) // (dashLenght+dashGap)
            DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
            StartGap = (roadLenght-DashedDist)//2
            dashStart = roadX + StartGap
            for j in range(1, roadObj.lanes): 
                dashY = roadY + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
                DashesNo = int(roadLenght) // (dashLenght+dashGap)
                dashStartPos = dashStart
                for i in range(0,DashesNo):
                    pygame.draw.line(screen,(255,255,255), (dashStartPos, dashY), (dashStartPos+dashLenght, dashY), DASHES_WIDTH)
                    dashStartPos += (dashLenght+dashGap)


        elif roadObj.orientation == 1:
            roadX = roadObj.cordinates[0] * SCALE_PER_M
            roadY = roadObj.cordinates[1] * SCALE_PER_M
            roadLenght = roadObj.lenght * SCALE_PER_M 
            roadWidth = (roadObj.lanes * LANE_WIDTH * SCALE_PER_M) + (roadObj.lanes - 1) * DASHES_WIDTH
            roadSize = (roadX, roadY, roadWidth, roadLenght)
            pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

            dashLenght = 3 * SCALE_PER_M
            dashGap = 6 * SCALE_PER_M
            DashesNo = int(roadLenght) // (dashLenght+dashGap)
            DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
            StartGap = (roadLenght-DashedDist)//2
            dashStart = roadY + StartGap
            for j in range(1, roadObj.lanes): 
                dashX = roadX + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
                DashesNo = int(roadLenght) // (dashLenght+dashGap)
                dashStartPos = dashStart
                for i in range(0,DashesNo):
                    pygame.draw.line(screen,(255,255,255), (dashX, dashStartPos), (dashX, dashStartPos+dashLenght), DASHES_WIDTH)
                    dashStartPos += (dashLenght+dashGap)
                    


# car1 = car("A01", "AA01", 5, 0, 45, 0) 

        
        for carObj in ActiveCarsNow:
            carRoad = ActiveRoadsList[carObj.current_road ]
            if carRoad.orientation == 0:
                carSCLength = carObj.car_length * SCALE_PER_M
                carX = (carRoad.cordinates[0] * SCALE_PER_M) + (carObj.X_position * SCALE_PER_M) - (carSCLength)
                carSCWidth = carWidth * SCALE_PER_M
                carY = (carRoad.cordinates[1] * SCALE_PER_M) + (((LANE_WIDTH * SCALE_PER_M) - carSCWidth)/2) + (DASHES_WIDTH * carObj.lane_No) + (LANE_WIDTH * SCALE_PER_M * carObj.lane_No)
                 #2st bracket = finds the space on 1 side of the car
                 #3nd bracket =  finds the space added due to dashes
                 #4rd bracket = finds the space added due to different lanes
                pygame.draw.rect(screen, color=(255,0,0), rect=(carX, carY, carSCLength, carSCWidth))

            elif carRoad.orientation == 1:
                carSCLength = carObj.car_length * SCALE_PER_M
                carY = (carRoad.cordinates[1] * SCALE_PER_M) + (carObj.X_position * SCALE_PER_M) - (carSCLength)
                carSCWidth = carWidth * SCALE_PER_M
                carX = (carRoad.cordinates[0] * SCALE_PER_M) + (((LANE_WIDTH * SCALE_PER_M) - carSCWidth)/2) + (DASHES_WIDTH * carObj.lane_No) + (LANE_WIDTH * SCALE_PER_M * carObj.lane_No)
                 #2st bracket = finds the space on 1 side of the car
                 #3nd bracket =  finds the space added due to dashes
                 #4rd bracket = finds the space added due to different lanes
                pygame.draw.rect(screen, color=(255,0,0), rect=(carX, carY, carSCWidth, carSCLength))

    # + (LANE_WIDTH * roadObj.lane_No) 

    #updates the display
    pygame.display.flip()

pygame.quit()