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
from Active_Lists.ActiveList import ActiveCarsNow, ActiveRoadsList, ActiveNodesDict
from Simulation import *
from heapq import heappush, heapify, heappop
import heapq
import sys


class car():
    
    def __init__(self, graph, carID, roadID, X_pos, laneNO, speed, acc,spawn, destinationList, carLenght):

        self.car_id = carID
        self.car_length = carLenght

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
        self.spawn = spawn #AvailableDestinations[spawn_location]
        self.destinationList = destinationList
        self.destination = destinationList[0] #AvailableDestinations[destination_location]
        self.routing_preference = random.randint(0, 1)
        #0: Less Distance
        #1: Less time
        self.route = self.pathFinder(graph, self.spawn, self.destination)
        
        #only appends in the list if the spawna and destination are reachable
        if self.route:
            print("route found")
            self.roadRoute = self.roadPath(graph)
            if self.roadRoute and self.roadRoute[0] == self.current_road:
                ActiveCarsNow.append(self)
            else:
                print("Bad route")
        else:
            print("NP")

    def minGapCalc(self):
        speed = self.current_speed/3.6        
        return driverConstants[self.driving_style]['BASE_GAP'] + (driverConstants[self.driving_style]['GAP_CONSTANT'] * self.reaction_time)*speed
        
    def carAheadDataFind(self):
        roadData = ActiveRoadsList[self.current_road]
        roadLimit = ActiveRoadsList[self.current_road].speed_limit
        laneData = roadData.cars_data[self.lane_No]

        # from that 2d list takes the data for that specific lane
        numberOfCars = len(laneData)
        #finds the number of cars on that lane

        currentCarId = None
        #default None just in case after a turn a car hasnt been added yet

        # iterates through the lane data, and finds the position of the car in that lane
        for i in range(numberOfCars):
            if laneData[i].car_id == self.car_id:
                currentCarId = i
                break

        # target_turn_distance = self.roadRoute.get(self.current_road, roadData.lenght)
        target_turn_distance = roadData.lenght
        
        if currentCarId is None:
            gap = target_turn_distance - self.X_position
            return {'Speed' : roadLimit, 'Gap': gap}

        currentCarXpos = laneData[currentCarId].X_position 
        if currentCarId != 0:
            carAheadXpos = laneData[currentCarId-1].X_position 
            carAheadLen = laneData[currentCarId-1].car_length
            
            gap = (carAheadXpos - carAheadLen) - currentCarXpos
            carAheadSpeed = laneData[currentCarId-1].current_speed
        else:
            gap = target_turn_distance - currentCarXpos
            carAheadSpeed = roadLimit

        return {'Speed' : carAheadSpeed, 'Gap': gap}
        #if there is no car ahead of a car it calculates the gap from the end of the road

    def carAccelerate(self, timeframe):
        carAheadData = self.carAheadDataFind()
        aheadSpeed = carAheadData["Speed"]/3.6 #in m/s
        gap = carAheadData["Gap"]
        if  gap < self.safety_margin:

            ''' ###### BRAKE ###### '''

            # print("braking")
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
                                                    timeframe
                                                    )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

        elif gap > self.safety_margin:

            ''' ###### ACCELERATE ###### '''

            # print("accelerate")
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
                                                        timeframe
                                                        )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

    def Acceleration_Working(self, CarAheadSpeed, SpeedMultiplier, constantStype, timeframe):
        #this gives the randomized target speed
        targetSpeed = CarAheadSpeed * SpeedMultiplier
        roadLimit = ActiveRoadsList[self.current_road].speed_limit
        limit_SI = min(self.max_speed, roadLimit) / 3.6
        targetSpeed = min(targetSpeed, limit_SI)
        
        #defined in Simulation.py, this is a driver property whch tells how much to accelerate per timeframe
        acc_contant = driverConstants[self.driving_style][constantStype]

        currentSpeedSI = self.current_speed/3.6 #in m/s

        #formula for finding the target speed for the current timeframe
        frameTargetSpeed = currentSpeedSI + acc_contant*(targetSpeed-currentSpeedSI)

        #based on the current frame target speed the acceleration required
        requiredAcceleration = (frameTargetSpeed - currentSpeedSI)/timeframe
        requiredAcceleration = max(-self.max_braking, min(self.max_acceleration, requiredAcceleration))

        newSpeedSI = max(0.0, currentSpeedSI + requiredAcceleration * timeframe)
        distance_travelled = currentSpeedSI * timeframe + 0.5 * requiredAcceleration * timeframe**2
        
        return {'Speed' : round(newSpeedSI * 3.6,3), 
                'Acc' : round(requiredAcceleration,3),
                'Distance' : round(distance_travelled,3)}
    
    def pathFinder(self, graph, start, destination):
        try:
            NodeDist = {}
            inf = sys.maxsize
            for node in graph.keys():
                NodeDist[node] = {"cost" : inf, "pred" : ""}
        
            NodeDist[start]['cost'] = 0
            VisitedNodes = []
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
                            dist = ActiveRoadsList[roadName].lenght
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
        except:
            return None

    def roadPath(self, graph):
        #list of all the roadIds the car needs to travel
        route = self.route
        transition = []
        for i in range(len(route)-1):
            roadID = graph[route[i]].get(route[i+1])
            if roadID is None:
                return None
            transition.append(roadID)
        return transition
    # def compulsoryBraking(self):

    def turn(self):
        roadRoute = (self.roadRoute)
        roadID = self.current_road
        roadLen = ActiveRoadsList[roadID].lenght
        
        if roadID == self.destinationList[1] and self.X_position >= self.destinationList[2] - 5:
            if self in ActiveCarsNow:
                print("deleting")
                ActiveCarsNow.remove(self)
            return


        elif self.X_position >= roadLen - 5:
            currentIndex = roadRoute.index(roadID)            
            if currentIndex+1 < len(roadRoute):
                next_road = roadRoute[currentIndex+1]
                overshoot = max(0.0, self.X_position - roadLen)
                self.current_road = next_road
                self.X_position = overshoot
                self.lane_No = random.randint(0, int(ActiveRoadsList[next_road].lanes)-1)
                print("Turning")
            else: 
                if self in ActiveCarsNow:
                    ActiveCarsNow.remove(self)
            

        # elif abs(self.X_position - roadRoute.get(roadID)) < 10:
        #             # car slows down
        #             print("SLOW")
