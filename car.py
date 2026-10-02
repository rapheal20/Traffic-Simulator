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
from roads import roads
from ActiveCars import ActiveCarsNow
from ActiveRoads import ActiveRoadsList
from Simulation import *



class car():
    
    def __init__(self, carID, roadID, X_pos, laneNO, speed, acc):

        self.car_id = carID
        self.car_length = 5


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
        self.spawn = AvailableDestinations[spawn_location]
        self.destination = AvailableDestinations[destination_location]
        self.routing_preference = random.randint(0, 1)
        #0: Less Distance
        #1: Less time
        self.route = []


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
            #brake
            if gap <= (0.5 * self.safety_margin):
                #very small gap so emergency braking
                targetSpeedMultiplier = round(random.uniform(0.8, 1),3)
            elif gap <= (0.75 * self.safety_margin):
                #small gap so hard braking
                targetSpeedMultiplier = round(random.uniform(0.95, 1.05),3)
            elif gap <= (0.9 * self.safety_margin):
                #smaller gap then 150% so smaller speed increment 0.9 to 1.0
                targetSpeedMultiplier = round(random.uniform(0.9, 1.0),3)

            #this gives the randomized target speed
            targetSpeed = aheadSpeed * targetSpeedMultiplier
            #defined in Simulation.py, this is a driver property whch tells how much to accelerate per timeframe
            acc_contant = driverConstants[self.driving_style]['ACC_CONSTANT']

            currentSpeedSI = self.current_speed/3.6 #in m/s
            #formula for finding the target speed for the current timeframe
            frameTargetSpeed = currentSpeedSI + acc_contant*(targetSpeed-currentSpeedSI)
            #based on the current frame target speed the acceleration required
            requiredAcceleration = (frameTargetSpeed - currentSpeedSI)/timeframe

            #checks if the acceleration is more then that the car can handle, if so then the required acceleration is the maximum supported by the car
            if requiredAcceleration > self.max_acceleration:
                requiredAcceleration = self.max_acceleration

            #updates the speed, acceleration and position
            self.current_speed = frameTargetSpeed*3.6 #converted back into KmH
            self.current_acceleration = requiredAcceleration

            distance_travelled = currentSpeedSI * timeframe + 0.5 * requiredAcceleration * timeframe**2
            self.X_position += distance_travelled #adds into the previous position
        elif gap > self.safety_margin:


            #accelerate
            if gap >= (1.5 * self.safety_margin):
                #bigger gap then 150% so greater speed increment 1 to 1.1
                targetSpeedMultiplier = round(random.uniform(1.0, 1.1),3)
            elif gap >= (1.1 * self.safety_margin):
                #bigger gap then 110% so normal speed increment 0.95 to 1.05
                targetSpeedMultiplier = round(random.uniform(0.95, 1.05),3)
            else:
                #smaller gap then 150% so smaller speed increment 0.9 to 1.0
                targetSpeedMultiplier = round(random.uniform(0.9, 1.0),3)

            #this gives the randomized target speed
            targetSpeed = aheadSpeed * targetSpeedMultiplier
            #defined in Simulation.py, this is a driver property whch tells how much to accelerate per timeframe
            acc_contant = driverConstants[self.driving_style]['ACC_CONSTANT']

            currentSpeedSI = self.current_speed/3.6 #in m/s
            #formula for finding the target speed for the current timeframe
            frameTargetSpeed = currentSpeedSI + acc_contant*(targetSpeed-currentSpeedSI)
            #based on the current frame target speed the acceleration required
            requiredAcceleration = (frameTargetSpeed - currentSpeedSI)/timeframe

            #checks if the acceleration is more then that the car can handle, if so then the required acceleration is the maximum supported by the car
            if requiredAcceleration > self.max_acceleration:
                requiredAcceleration = self.max_acceleration

            #updates the speed, acceleration and position
            self.current_speed = frameTargetSpeed*3.6 #converted back into KmH
            self.current_acceleration = requiredAcceleration

            distance_travelled = currentSpeedSI * timeframe + 0.5 * requiredAcceleration * timeframe**2
            self.X_position += distance_travelled #adds into the previous position


        else:
            #maintain
            print()
        




road1 = roads(
                roadID= 'AA01',
                roadLength = 500,
                lanes = 2,
                speedLimit = 60,
                oneWay = True,
                locationsAvailable = [0, 250, 500],
                trafficLight = 500,
                )

road2 = roads(
                roadID= 'BB01',
                roadLength = 500,
                lanes = 2,
                speedLimit = 60,
                oneWay = True,
                locationsAvailable = [0, 250, 500],
                trafficLight = 500,
                )


# car1 = car("A01", 'AA01', 98, 0)
# car2 = car("A02", 'AA01', 67, 0)
# car3 = car("B01", 'AA01', 56, 0)
# car4 = car("B02", 'AA01', 230, 0)
# car5 = car("B03", 'AA01', 75, 0)
# car6 = car("B04", 'AA01', 310, 0)
# car7 = car("B05", 'AA01', 145, 0)
# car8 = car("B06", 'AA01', 25, 0)
# car9 = car("B07", 'AA01', 275, 0)
# car10 = car("B08", 'AA01', 190, 0)
# car11 = car("B09", 'AA01', 355, 0)
# car12 = car("B10", 'AA01', 115, 0)
# car13 = car("B11", 'AA01', 265, 0)




car1 = car("A01", 'AA01', 98, 0, 52, 0)
car2 = car("A02", 'AA01', 67, 0, 47, 0)
car3 = car("B01", 'AA01', 56, 0, 43, 0)
car4 = car("B02", 'AA01', 230, 0, 58, 0)
car5 = car("B03", 'AA01', 75, 0, 50, 0)
car6 = car("B04", 'AA01', 25, 0, 38, 0)
car7 = car("B05", 'AA01', 145, 0, 45, 0)
car8 = car("B06", 'AA01', 190, 0, 55, 0)
car9 = car("B07", 'AA01', 275, 0, 42, 0)
car10 = car("B08", 'AA01', 115, 0, 48, 0)
car11 = car("B09", 'AA01', 355, 0, 60, 0)
car12 = car("B10", 'AA01', 310, 0, 35, 0)
car13 = car("B11", 'AA01', 265, 0, 53, 0)
# print(ActiveCarsNow)

# # print(ActiveCarsNow[1].car_id)
road1.activeCarsList()
# car1.carAheadGapFind()


# # print(road1.cars_data)

for i in road1.cars_data[0]:
    print("Car Start")
    print(i.car_id, i.lane_No, i.X_position, i.current_speed, i.current_acceleration)
    print(i.carAheadDataFind())
    print(i.carAccelerate())
    print(i.car_id, i.lane_No, i.X_position, i.current_speed, i.current_acceleration)
    

# for i in road1.cars_data[1]:
#     print(i.car_id, i.lane_No, i.X_position)



# for i in range(15):
#     car1 = car()
#     # print(car1.max_speed, car1.max_acceleration, car1.max_braking, car1.car_priority,car1.driving_style,car1.reaction_time)
#     print(vars(car1))