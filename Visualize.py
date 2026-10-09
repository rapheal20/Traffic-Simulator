import pygame

pygame.init()

screen = pygame.display.set_mode((1366,768))

# Conversion: 1m = 5px


from car import road1, road2
from ActiveRoads import ActiveRoadsList
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
    screen.fill((255,255,255))
    for roadObj in ActiveRoadsList.values():
        if roadObj.orientation == 0:
            roadX = roadObj.cordinates[0] * SCALE_PER_M
            roadY = roadObj.cordinates[1] * SCALE_PER_M
            roadLenght = roadObj.lenght * SCALE_PER_M
            roadWidth = roadObj.lanes * LANE_WIDTH * SCALE_PER_M + (roadObj.lanes - 1) * DASHES_WIDTH
            roadSize = (roadX, roadY, roadLenght, roadWidth)
            pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

            #road dashes
            dashStart = roadX + 15
            for j in range(1, roadObj.lanes + 1): 
                dashY = roadY + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
                for i in range(0,roadLenght+1,30):
                    dashStartPos = dashStart + i
                    pygame.draw.line(screen,(255,255,255), (dashStartPos, dashY), (dashStartPos+15, dashY), DASHES_WIDTH)


        elif roadObj.orientation == 1:
            roadX = roadObj.cordinates[0] * SCALE_PER_M
            roadY = roadObj.cordinates[1] * SCALE_PER_M
            roadLenght = roadObj.lenght * SCALE_PER_M 
            roadWidth = (roadObj.lanes * LANE_WIDTH * SCALE_PER_M) + (roadObj.lanes - 1) * DASHES_WIDTH
            roadSize = (roadX, roadY, roadWidth, roadLenght)
            pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

            dashStart = roadY + 15
            for j in range(1, roadObj.lanes + 1): 
                dashX = roadX + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
                for i in range(0,roadLenght+1,30):
                    dashStartPos = dashStart + i
                    pygame.draw.line(screen,(255,255,255), (dashX, dashStartPos), (dashX, dashStartPos+15), DASHES_WIDTH)



        
    # x_end = 40
    # x_start = 20

    # while x_end < roadSize[2]:
    #     
    #     pygame.draw.line(screen,(255,255,255), (x_start, 220), (x_end, 220), 3)
    #     x_start = (20 + x_end)
    #     x_end += 40
        
    #1 lane is 60 px

    # pygame.draw.rect(screen, color=(255,0,0), rect=(25, 107,100,45))

    #updates the display
    pygame.display.flip()

pygame.quit()