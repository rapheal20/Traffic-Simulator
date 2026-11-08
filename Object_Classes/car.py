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
    
    def __init__(self, carID, roadID, X_pos, laneNO, speed, acc, destination):

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
        # self.spawn = spawn #AvailableDestinations[spawn_location]
        self.destination = destination #AvailableDestinations[destination_location]
        self.routing_preference = random.randint(0, 1)
        #0: Less Distance
        #1: Less time
        self.route = self.pathFinder(graph, self.spawn, self.destination)

        self.roadRoute = self.roadPath(graph)

        ActiveCarsNow.append(self)

        

    def minGapCalc(self):
        speed = self.current_speed/3.6        
        return driverConstants[self.driving_style]['BASE_GAP'] + (driverConstants[self.driving_style]['GAP_CONSTANT'] * self.reaction_time)*speed
        
    def carAheadDataFind(self):
        roadData = ActiveRoadsList[self.current_road]
        #gets the lis tof cars on the road
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

        target_turn_distance = self.roadRoute.get(self.current_road, roadData.lenght)
        
        if not currentCarId:
            gap = target_turn_distance - self.X_position
            return {'Speed' : 60, 'Gap': gap}

        currentCarXpos = laneData[currentCarId].X_position 
        if i != 0:
            carAheadXpos = laneData[currentCarId-1].X_position 
            carAheadLen = laneData[currentCarId-1].car_length
            
            gap = (carAheadXpos - carAheadLen) - currentCarXpos
            carAheadSpeed = laneData[currentCarId-1].current_speed
        else:
            gap = target_turn_distance - currentCarXpos
            carAheadSpeed = 60

        return {'Speed' : carAheadSpeed, 'Gap': gap}
        #if there is no car ahead of a car it calculates the gap from the end of the road

    def carAccelerate(self, timeframe):
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
                                                    self.max_braking,
                                                    timeframe
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
                                                        self.max_acceleration,
                                                        timeframe
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
                                                        self.max_acceleration,
                                                        timeframe
                                                        )
            # print(gap, self.safety_margin)
            self.current_speed = Updated_Data['Speed']
            self.current_acceleration = Updated_Data['Acc']
            self.X_position += Updated_Data['Distance']

    def Acceleration_Working(self, CarAheadSpeed, SpeedMultiplier, constantStype, operationType, timeframe):
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
                        
                        
                        if currentNode in ActiveRoadsList[roadName].nodes and j in ActiveRoadsList[roadName].nodes:
                            dist = abs(ActiveRoadsList[roadName].nodes[currentNode] - ActiveRoadsList[roadName].nodes[j])
                            #here it subtracts the distance of 2 nodes on the road to get the actual distance
                        else:
                            dist = ActiveRoadsList[roadName].lenght
                            #if both the nodes are not on the same road them it uses the lenght of the road as the distance
                        
                        
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

    def roadPath(self, graph):
        #path making

        # {
        #     "AA01" : 25,
        #     "BB01" : 60,
        #     "AA02": 100
        # }

        #main dictioanry obj, has the distance it has to travel on each road


        route = self.route
        transition = {}
        initialized = False
        currentNode = route[0]

        if self.current_road in ActiveNodesDict[currentNode].roadsConnected and not initialized:
            initialized = True
            turnDistance = ActiveRoadsList[self.current_road].nodes[currentNode]
            transition[self.current_road] = turnDistance

        for i in range(len(route)-1):
            currentNode = route[i]
            nextNode = route[i+1]


            # gets the dictionary at currentNode, if not found default {}
            # from that dict gets the roadID of the next node
            roadID = graph.get(currentNode, {}).get(nextNode)

            if roadID and roadID in ActiveRoadsList:
                roadObj = ActiveRoadsList[roadID]

                if nextNode in roadObj.nodes:
                    turnDistance = roadObj.nodes[nextNode]
                    transition[roadID] = turnDistance
                else:
                    transition[roadID] = roadObj.lenght

        return transition

    # def compulsoryBraking(self):

    def turn(self):
        roadRoute = (self.roadRoute)
        roadID = self.current_road
        
        # print(self.X_position, roadRoute.get(roadID))
        if abs(self.X_position - roadRoute.get(roadID)) < 5:

            routeList = (list(roadRoute.keys()))
            currentIndex = routeList.index(roadID)
            print(routeList)
            
            if currentIndex+1 < len(routeList):
                next_road = routeList[currentIndex+1]

                if self.current_road != next_road:
                    self.current_road = next_road
                    startPos = 0.0

                    #checks for the node offset and then positions the car there
                    for nodeId, nodeOffset in ActiveRoadsList[next_road].nodes.items():
                        if nodeId in self.route:
                            startPos = nodeOffset
                            break
                    laneNumbers = ActiveRoadsList[next_road].lanes
                    NewLane = random.randint(0, laneNumbers-1)

                    self.lane_No = NewLane
                    self.X_position = startPos
                    print(self.current_road)
                    print("Turning")
            else: 
                print("Reached")
                if self in ActiveCarsNow:
                    ActiveCarsNow.remove(self)

        # elif abs(self.X_position - roadRoute.get(roadID)) < 10:
        #             # car slows down
        #             print("SLOW")
