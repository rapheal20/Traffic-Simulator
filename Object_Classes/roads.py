from Active_Lists.ActiveList import ActiveRoadsList, ActiveNodesDict, ActiveNodesSet

class roads():


    def __init__(self, roadID, coordinates, roadLength, lanes, oneway, speedLimit, unitVec, normal, startNode, endNode):
        self.road_id = roadID
        self.coordinates = coordinates #list of tuple
        self.lenght = roadLength #real
        self.lanes = int(round(lanes,0)) #integer
        self.speed_limit = speedLimit #integer
        self.oneway = oneway #Boolean
        self.UnitVector = unitVec
        self.NormalVector = normal
        self.StartNode = startNode
        self.EndNode = endNode

        self.cars_data = [[] for _ in range(self.lanes)]


        ActiveRoadsList[self.road_id] = self

    

    # def activeCarsList(self):
    #     #in a list this function arranges the cars such that the car furthest from the starting point is at the 0 index, so the car that just began moving on the road is the last index


    #     for i in range(len(ActiveCarsNow)):
    #         if ActiveCarsNow[i].current_road == self.road_id:
    #             laneNumber = ActiveCarsNow[i].lane_No #extracts the lane number from the car at the active index
    #             lenghtOfList = len(self.cars_data[laneNumber]) #takes the lenght of the list at the specified lane number, ie number of cars in one lane
    #             currentCarXpos = ActiveCarsNow[i].X_position #extracts the x position of the car at the active index


    #             if lenghtOfList >= 2:
    #                 locationFound = False
    #                 j = 0
    #                 while not locationFound and j < (lenghtOfList-1):


    #                     jCarXpos = self.cars_data[laneNumber][j].X_position #extracts the x position of the car at position j
    #                     j1CarXpox = self.cars_data[laneNumber][j+1].X_position #extracts the x position of the car at position j + 1


    #                     if currentCarXpos > jCarXpos: #checks if the current car position is greater then the largest index
    #                         self.cars_data[laneNumber].insert(j,ActiveCarsNow[i])  #if iyes inserts before it
    #                         locationFound = True

                        
    #                     elif currentCarXpos > j1CarXpox: #check if current car is bigger then car at J + 1
    #                         self.cars_data[laneNumber].insert(j+1,ActiveCarsNow[i]) #inserts before it 
    #                         locationFound = True
                            
    #                     else:
    #                         if j == lenghtOfList-2: #checks if the maximum value of J is achieved if so and still no place is foud for the car it appends at the end
    #                             self.cars_data[laneNumber].append(ActiveCarsNow[i])
    #                     j+=1
    #             elif len(self.cars_data[laneNumber]) == 1: #followed in case the list has only one car, compare where it fits in and adds it
    #                     if currentCarXpos < self.cars_data[laneNumber][0].X_position:
    #                         self.cars_data[laneNumber].append(ActiveCarsNow[i])
    #                     else:
    #                         self.cars_data[laneNumber].insert(0,ActiveCarsNow[i])
    #             else:   #followed is the lsit is empty, jsut appends it
    #                 self.cars_data[laneNumber].append(ActiveCarsNow[i])
