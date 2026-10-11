import pygame
import ObjectCreations
from Active_Lists.ActiveRoads import ActiveRoadsList
from Active_Lists.ActiveCars import ActiveCarsNow
# from Visualize import *
pygame.init()

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1366
BG_COLOR = (227, 227, 227)     # Dark gray background
GRID_COLOR = (182, 182, 182)    #light gray
CELL_SIZE = 50
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
elapsed = 0


camera_X = 0
camera_Y = 0
is_dragging = False
last_mouse_pos = (0,0)  
#camera_X and camera_Y are the anchors of the screen
#they are used to find out how far adn where the screen is dragged
#last_mouse_pos keeps the last postion of the mouse to calculaet the change  


SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.000529 #in m   2px


carWidth = 1.8
carLenght = 4.5


zoom_scale = 1.0
MIN_ZOOM = 0.2
MAX_ZOOM = 5.0

running = True
while running:


    


    #pygame.event.get() returns all the events happening
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

            if zoom_scale > MAX_ZOOM:
                zoom_scale = MAX_ZOOM
            elif zoom_scale < MIN_ZOOM:
                zoom_scale = MIN_ZOOM   

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

    def drawRoads():
        CURRENT_ZOOM = SCALE_PER_M * zoom_scale
        NEW_DASH_WIDTH = int(round((2 * zoom_scale), 0))
        # LANE_WIDTH = LANE_WIDTH * CURRENT_ZOOM
        # if NEW_DASH_WIDTH % 2 != 0:
        #     NEW_DASH_WIDTH+=1

        # print(NEW_DASH_WIDTH)


        # start_X = camera_X % CURRENT_ZOOM
        # start_Y = camera_Y % CURRENT_ZOOM


        for roadObj in ActiveRoadsList.values():
            if roadObj.orientation == 0:
                roadX = roadObj.cordinates[0] * CURRENT_ZOOM
                roadY = roadObj.cordinates[1] * CURRENT_ZOOM
                roadLenght = roadObj.lenght * CURRENT_ZOOM
                roadWidth = roadObj.lanes * LANE_WIDTH * zoom_scale + (roadObj.lanes - 1) * NEW_DASH_WIDTH

                # roadWidth = round(roadWidth,0)
                # if roadWidth % 2 != 0:
                #     roadWidth+=1

                #pan Values
                roadX = int(camera_X + roadX)
                roadY = int(camera_Y + roadY)
                roadSize = (roadX, roadY, roadLenght, roadWidth)
                pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

                #road dashes
                dashLenght = 3 * CURRENT_ZOOM
                dashGap = 6 * CURRENT_ZOOM
                DashesNo = int(roadLenght) // (dashLenght+dashGap)
                DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
                StartGap = (roadLenght-DashedDist)//2
                dashStart = roadX + StartGap
                Lane_Calc_Width = (roadWidth - ((roadObj.lanes - 1) * NEW_DASH_WIDTH))/roadObj.lanes


                for j in range(1, roadObj.lanes): 
                    dashY = round(roadY + (LANE_WIDTH*CURRENT_ZOOM)*j + (NEW_DASH_WIDTH)*(j-1))

                    
                    # print((Lane_Calc_Width)*j + (NEW_DASH_WIDTH)*(j-1))
                    DashesNo = int(roadLenght//(dashLenght+dashGap))
                    dashStartPos = dashStart
                    for i in range(0,DashesNo):
                        pygame.draw.line(screen,(255,255,255), (dashStartPos, dashY), (dashStartPos+dashLenght, dashY), (NEW_DASH_WIDTH))
                        dashStartPos += (dashLenght+dashGap)


            # elif roadObj.orientation == 1:
            #     roadX = roadObj.cordinates[0] * SCALE_PER_M
            #     roadY = roadObj.cordinates[1] * SCALE_PER_M
            #     roadLenght = roadObj.lenght * SCALE_PER_M 
            #     roadWidth = (roadObj.lanes * LANE_WIDTH * SCALE_PER_M) + (roadObj.lanes - 1) * DASHES_WIDTH
            #     roadSize = (roadX, roadY, roadWidth, roadLenght)
            #     pygame.draw.rect(surface=screen,color=(0,0,0), rect=roadSize)

            #     dashLenght = 3 * SCALE_PER_M
            #     dashGap = 6 * SCALE_PER_M
            #     DashesNo = int(roadLenght) // (dashLenght+dashGap)
            #     DashedDist = dashLenght*DashesNo + dashGap*(DashesNo-1)
            #     StartGap = (roadLenght-DashedDist)//2
            #     dashStart = roadY + StartGap
            #     for j in range(1, roadObj.lanes): 
            #         dashX = roadX + (LANE_WIDTH * SCALE_PER_M)*j + DASHES_WIDTH*(j-1)
            #         DashesNo = int(roadLenght) // (dashLenght+dashGap)
            #         dashStartPos = dashStart
            #         for i in range(0,DashesNo):
            #             pygame.draw.line(screen,(255,255,255), (dashX, dashStartPos), (dashX, dashStartPos+dashLenght), DASHES_WIDTH)
            #             dashStartPos += (dashLenght+dashGap)
                        




    drawGrid()
    # drawRoads()
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
