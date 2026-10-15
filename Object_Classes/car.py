# Car structure
# 
# Car
# │
# ├── Physical properties
# │   ├── max_speed
# │   ├── max_acceleration
# │   └── max_braking
# │
# ├── Current state
# │   ├── position
# │   ├── speed
# │   ├── acceleration
# │   └── lane
# │
# ├── Driver properties
# │   ├── driving_style
# │   ├── reaction_time
# │   └── safety_margin
# │
# ├── Trip information
# │   ├── destination
# │   ├── route
# │   └── routing_preference
# │
# └── Methods
#     ├── observe()
#     ├── decide()
#     ├── accelerate()
#     ├── brake()
#     ├── move()
#     └── change_lane()

import random
# from Object_Classes.roads import roads
from Active_Lists.ActiveCars import ActiveCarsNow
from Active_Lists.ActiveRoads import ActiveRoadsList
from Simulation import *
from heapq import heappush, heapify, heappop
import heapq
import sys
# from ObjectCreations import graph
# from ObjectCreations import *


graph = {
    "N01" : {"N02" :"AA01", "N03":"BB01"},
    "N02" : {"N05" :"BB03", "N07" : "BB03"},
    "N03" : {"N04" :"AA02", "N05":'AA02'},
    "N04" : {"N05" :"AA02", "N06":"BB02"},
    "N05" : {"N07" :"BB03"},
    "N06" : {"N07" :"AA03"},
    "N07" : {}
}


class car():
    
    def __init__(self, carID, roadID, X_pos, laneNO, speed, acc, spawn, destination):

        self.car_id = carID
        self.car_length = 4.5


        #Car Physical properties
        max_speed_list = [120, 130, 140, 150, 160, 170, 180]
        self.max_speed = max_speed_list[random.randint(0, 6)]
        self.max_acceleration = round(random.uniform(2.0,4.0), 4)
        self.max_braking = round(random.uniform(7.0,9.0), 4)

        emergencycar = random.randint(1,10)
        if emergencycar > 2:
            self.car_priority = 0
        else:
            self.car_priority = 1
        # 0 : Normal Car
        # 1 : Emergency Vehicle
        # 80% of the cars are normal


        #Spawn Data

        #the xpos is the distance of the car`s front bumper to the start of the road, gap is bumper to bumper
        self.current_road = roadID
        self.X_position = X_pos
        self.lane_No = laneNO
        self.current_speed = speed
        self.current_acceleration = acc

        
        #Driver properties

        # Driving Style:
        # 0 = Aggressive
        # 1 = Calm
        # 2 = Nervous
        self.driving_style = random.randint(0, 2)
        self.reaction_time = round(random.uniform(0.2, 2.0), 4)
        self.safety_margin = self.minGapCalc()


        #Routing Properties
        
        spawn_location = random.randint(0, len(AvailableDestinations)-1)
        destination_location = random.randint(0, len(AvailableDestinations)-1)
        while spawn_location == destination_location:
            destination_location = random.randint(0, len(AvailableDestinations)-1)
        self.spawn = spawn #AvailableDestinations[spawn_location]
        self.destination = destination #AvailableDestinations[destination_location]
        self.routing_preference = random.randint(0, 1)
        #0: Less Distance
        #1: Less time
        self.route = self.pathFinder(graph, self.spawn, self.destination)


        ActiveCarsNow.append(self)

        

    def minGapCalc(self):
        speed = self.current_speed/3.6        
        return driverConstants[self.driving_style]['BASE_GAP'] + (driverConstants[self.driving_style]['GAP_CONSTANT'] * self.reaction_time)*speed
        
    def carAheadDataFind(self):
        roadData = ActiveRoadsList[self.current_road]
        laneData = roadData.cars_data[self.lane_No]
        numberOfCars = len(laneData)
        for i in range(numberOfCars):
            if laneData[i].car_id == self.car_id:
                currentCarId = i
                break
        currentCarXpos = laneData[currentCarId].X_position 
        if i != 0:
            carAheadXpos = laneData[currentCarId-1].X_position 
            carAheadLen = laneData[currentCarId-1].car_length
            
            gap = (carAheadXpos - carAheadLen) - currentCarXpos
            carAheadSpeed = laneData[currentCarId-1].current_speed
        else:
            gap = roadData.lenght - currentCarXpos
            carAheadSpeed = -1

        return {'Speed' : carAheadSpeed, 'Gap': gap}
        #if there is no car ahead of a car it calculates the gap from the end of the road

    def carAccelerate(self):
        carAheadData = self.carAheadDataFind()
        aheadSpeed = carAheadData["Speed"]/3.6 #in m/s
        gap = carAheadData["Gap"]
        if  gap < self.safety_margin:

            ''' ###### BRAKE ###### '''

            print("braking")
            if gap <= (0.5 * self.safety_margin):
                #very small gap so emergency braking (braking threshold = 85 to 90%)
                targetSpeedMultiplier = round(random.uniform(0.1, 0.25),3)
            elif gap <= (0.75 * self.safety_margin):
                #small gap so hard braking (braking threshold = 55 to 75%)
                targetSpeedMultiplier = round(random.uniform(0.25, 0.45),3)
            elif gap <= (0.9 * self.safety_margin):
                #not that small gap so normal braking (braking threshold = 25 to 40%)
                targetSpeedMultiplier = round(random.uniform(0.6, 0.75),3)
            else: 
                #ok gap so norvery little braking (braking threshold = 10 to 20%)
                targetSpeedMultiplier = round(random.uniform(0.8, 0.9),3)


            Updated_Data = self.Acceleration_Working(aheadSpeed,
                                                    targetSpeedMultiplier,
                                                    'BRAKING_CONSTANT',
                                                    self.max_braking
                                                    )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

        elif gap > self.safety_margin:

            ''' ###### ACCELERATE ###### '''

            print("accelerate")
            if gap >= (1.5 * self.safety_margin):
                #bigger gap then 150% so greater speed increment 1 to 1.1
                targetSpeedMultiplier = round(random.uniform(1.0, 1.1),3)
            elif gap >= (1.1 * self.safety_margin):
                #bigger gap then 110% so normal speed increment 0.95 to 1.05
                targetSpeedMultiplier = round(random.uniform(0.95, 1.05),3)
            else:
                #smaller gap then 110% so smaller speed increment 0.9 to 1.0
                targetSpeedMultiplier = round(random.uniform(0.9, 1.0),3)

            Updated_Data = self.Acceleration_Working(aheadSpeed,
                                                        targetSpeedMultiplier,
                                                        'ACC_CONSTANT',
                                                        self.max_acceleration
                                                        )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

        else:
        
            ''' ###### MAINTAIN ###### '''
            print("maintain")
            targetSpeedMultiplier = round(random.uniform(0.98, 1.02),3)

            #uses acceleration constant
            Updated_Data = self.Acceleration_Working(aheadSpeed,
                                                        targetSpeedMultiplier,
                                                        'ACC_CONSTANT',
                                                        self.max_acceleration
                                                        )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

    def Acceleration_Working(self, CarAheadSpeed, SpeedMultiplier, constantStype, operationType):
        #this gives the randomized target speed
        targetSpeed = CarAheadSpeed * SpeedMultiplier
        #defined in Simulation.py, this is a driver property whch tells how much to accelerate per timeframe
        acc_contant = driverConstants[self.driving_style][constantStype]

        currentSpeedSI = self.current_speed/3.6 #in m/s

        #formula for finding the target speed for the current timeframe
        frameTargetSpeed = currentSpeedSI + acc_contant*(targetSpeed-currentSpeedSI)

        #based on the current frame target speed the acceleration required
        requiredAcceleration = (frameTargetSpeed - currentSpeedSI)/timeframe

        #checks if the acceleration is more then that the car can handle, if so then the required acceleration is the maximum supported by the car
        
        if requiredAcceleration > operationType:
            requiredAcceleration = operationType

        #updates the speed, acceleration and position
        newSpeed = frameTargetSpeed*3.6 #converted back into KmH
        newAcc = requiredAcceleration

        # calculating distance travelled
        distance_travelled = currentSpeedSI * timeframe + 0.5 * requiredAcceleration * timeframe**2
        return {'Speed' : round(newSpeed,3), 
                'Acc' : round(newAcc,3),
                'Distance' : round(distance_travelled,3)}
    
    def pathFinder(self, graph, start, destination):
        NodeDist = {}
        inf = sys.maxsize
        for node in graph.keys():
            NodeDist[node] = {"cost" : inf, "pred" : ""}
        
        NodeDist[start]['cost'] = 0

        VisitedNodes = []
        tempSRC = start
        steps = len(graph) - 1 #it takes n-1 steps to complete
        min_heap = []  
        heappush(min_heap, (0, start))
        while min_heap:
            currentCost, currentNode = heappop(min_heap)
            if currentNode in VisitedNodes:
                continue #checks if currentNode is already visited, if it is then it skips the iteration

            VisitedNodes.append(currentNode)

            if currentNode == destination:
                #if the destination is reached, breaks the loop
                break
            else:
                for j in graph[currentNode]:
                    if j not in VisitedNodes:
                        roadName = (graph[currentNode][j])
                        dist = abs(
                            ActiveRoadsList[roadName].nodes[currentNode]
                            - ActiveRoadsList[roadName].nodes[j])
                        #here it subtracts the distance of 2 nodes on the road to get the actual distance
                        cost = currentCost + dist
                        if cost < NodeDist[j]['cost']:
                            NodeDist[j]['cost'] = cost #reassigns when the cost is lower
                            NodeDist[j]['pred'] = currentNode
                            heappush(min_heap, (NodeDist[j]['cost'], j)) #thsi creates a tuple type datatype list with the min distances adn their respective nodes
        path = []
        foundPred = NodeDist[destination]['pred']
        while foundPred != start:
            path.insert(0, foundPred)
            foundPred = NodeDist[foundPred]['pred']
        path.insert(0, start)
        path.append(destination)

        return path
        
# road1 = roads(
#                 roadID= 'AA01',
#                 cordinates= (25,25),
#                 roadLength = 60,
#                 lanes = 4,
#                 orientation=0,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [0, 250, 500],
#                 trafficLight = 60,
#                 )

# road2 = roads(
#                 roadID= 'BB01',
#                 cordinates= (60+25,0),
#                 roadLength = 60,
#                 lanes = 2,
#                 orientation=1,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [0, 250, 500],
#                 trafficLight = 50,
#                 )

# #all operations
# # car1 = car("A01", "AA01", 20, 0, 40, 0)
# # car2 = car("A02", "AA01", 23, 0, 45, 0)    # 3 m gap — decelerate

# # car3 = car("A03", "AA01", 40, 0, 35, 0)
# # car4 = car("A04", "AA01", 48, 0, 34, 0)    # 8 m gap — maintain (if within threshold)

# # car5 = car("A05", "AA01", 65, 0, 25, 0)
# # car6 = car("A06", "AA01", 82, 0, 30, 0)    # 17 m gap — accelerate

# # car7 = car("A07", "AA01", 100, 0, 55, 0)
# # car8 = car("A08", "AA01", 104, 0, 30, 0)  # 4 m gap — decelerate

# # car9 = car("A09", "AA01", 125, 0, 40, 0)
# # car10 = car("A10", "AA01", 135, 0, 39, 0)  # 10 m gap — maintain (if within threshold)

# # car11 = car("A11", "AA01", 160, 0, 20, 0)
# # car12 = car("A12", "AA01", 185, 0, 45, 0)  # 25 m gap — accelerate

# # car13 = car("A13", "AA01", 210, 0, 50, 0)
# # car14 = car("A14", "AA01", 213, 0, 15, 0)  # 3 m gap — decelerate

# # car15 = car("A15", "AA01", 240, 0, 35, 0)
# # car16 = car("A16", "AA01", 252, 0, 35, 0)  # 12 m gap — maintain (if within threshold)




# # car1 = car("A01", 'AA01', 98, 0, 52, 0)
# # car2 = car("A02", 'AA01', 67, 0, 47, 0)
# # car3 = car("B01", 'AA01', 56, 0, 43, 0)
# # car4 = car("B02", 'AA01', 230, 0, 58, 0)
# # car5 = car("B03", 'AA01', 75, 0, 50, 0)
# # car6 = car("B04", 'AA01', 25, 0, 38, 0)
# # car7 = car("B05", 'AA01', 145, 0, 45, 0)
# # car8 = car("B06", 'AA01', 190, 0, 55, 0)
# # car9 = car("B07", 'AA01', 275, 0, 42, 0)
# # car10 = car("B08", 'AA01', 115, 0, 48, 0)
# # car11 = car("B09", 'AA01', 355, 0, 60, 0)
# # car12 = car("B10", 'AA01', 310, 0, 35, 0)
# # car13 = car("B11", 'AA01', 265, 0, 53, 0)
# # print(ActiveCarsNow)



# #Test Data With Braking and Acc
# # car1 = car("A01", "AA01", 20, 0, 45, 0)
# # car2 = car("A02", "AA01", 22, 0, 40, 0)   # 2 m gap
# # car3 = car("A03", "AA01", 25, 0, 30, 0)   # 3 m gap
# # car4 = car("A04", "AA01", 29, 0, 55, 0)   # 4 m gap
# # car5 = car("A05", "AA01", 34, 0, 25, 0)   # 5 m gap
# # car6 = car("A06", "AA01", 42, 0, 50, 0)   # 8 m gap
# # car7 = car("A07", "AA01", 44, 0, 20, 0)   # 2 m gap
# # car8 = car("A08", "AA01", 46, 0, 60, 0)   # 2 m gap
# # car9 = car("A09", "AA01", 55, 0, 35, 0)   # 9 m gap
# # car10 = car("A10", "AA01", 70, 0, 50, 0)  # 15 m gap
# # car11 = car("A11", "AA01", 72, 0, 15, 0)  # 2 m gap
# # car12 = car("A12", "AA01", 90, 0, 40, 0)  # 18 m gap




# # ROAD AA01 — 4 lanes, 60 m long

# # ROAD AA01 — 4 lanes, 60 m long

# # Lane 0: close following, mixed speeds
# car1 = car("A01", "AA01", 5, 0, 45, 0)
# car2 = car("A02", "AA01", 12, 0, 30, 0)   # 2.6 m gap
# car3 = car("A03", "AA01", 25, 0, 55, 0)   # 8.6 m gap

# # Lane 1: close following
# car4 = car("A04", "AA01", 8, 1, 25, 0)
# car5 = car("A05", "AA01", 16, 1, 40, 0)   # 3.6 m gap
# car6 = car("A06", "AA01", 30, 1, 35, 0)   # 9.6 m gap

# # Lane 2: mixed speeds and larger gaps
# car7 = car("A07", "AA01", 6, 2, 50, 0)
# car8 = car("A08", "AA01", 20, 2, 20, 0)   # 9.6 m gap

# # Lane 3: close following and free-flow car
# car9 = car("A09", "AA01", 10, 3, 35, 0)
# car10 = car("A10", "AA01", 18, 3, 55, 0)  # 3.6 m gap
# car11 = car("A11", "AA01", 40, 3, 30, 0)  # 17.6 m gap


# # ROAD BB01 — 2 lanes, 60 m long

# # Lane 0: close following, mixed speeds
# car12 = car("B01", "BB01", 4, 0, 50, 0)
# car13 = car("B02", "BB01", 11, 0, 25, 0)  # 2.6 m gap
# car14 = car("B03", "BB01", 24, 0, 40, 0)  # 8.6 m gap
# car15 = car("B04", "BB01", 42, 0, 55, 0)  # 13.6 m gap

# # Lane 1: moderate and large gaps
# car16 = car("B05", "BB01", 8, 1, 30, 0)
# car17 = car("B06", "BB01", 18, 1, 45, 0)  # 5.6 m gap
# car18 = car("B07", "BB01", 32, 1, 20, 0)  # 9.6 m gap
# car19 = car("B08", "BB01", 48, 1, 50, 0)  # 11.6 m gap
# # # print(ActiveCarsNow[1].car_id)
# road1.activeCarsList()
# road2.activeCarsList()
# # car1.carAheadGapFind()


# # print(road1.cars_data)

# for i in road1.cars_data[0]:
#     print("Car Start")
#     print(f"{i.car_id}, {i.lane_No}, position {i.X_position}, speed {i.current_speed}, acc {i.current_acceleration}, driver {i.driving_style}")
#     (i.carAheadDataFind())
#     (i.carAccelerate())
#     print("Car Data New")
#     print(f"{i.car_id}, {i.lane_No}, position {i.X_position}, speed {i.current_speed}, acc {i.current_acceleration}")
#     print()

# for i in road1.cars_data[1]:
#     print(i.car_id, i.lane_No, i.X_position)



# for i in range(15):
#     car1 = car()
#     # print(car1.max_speed, car1.max_acceleration, car1.max_braking, car1.car_priority,car1.driving_style,car1.reaction_time)
#     print(vars(car1))




# car("A02", "AA01", 12, 0, 6, 0)