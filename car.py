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
class car():
    
    def __init__(self):
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
        self.X_postion = 32
        self.lane_No = 1
        self.current_speed = 43
        self.current_acceleration = 2.2

        
        #Driver properties

        # Driving Style:
        # 0 = Aggressive
        # 1 = Calm
        # 2 = Nervous
        self.driving_style = random.randint(0, 2)
        self.reaction_time = round(random.uniform(0.2, 2.0), 4)
        self.safety_margin = self.minGapCalc()




        #Routing Properties
        AvailableDestinations = ['W', 'X', 'Y', 'Z']
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


        

    def minGapCalc(self):
        speed = self.current_speed/3.6
        # base_gap = (speed * self.reaction_time) + ((speed*speed)/2*self.current_acceleration)
        # base_gap 
        
        if self.driving_style == 0:
            return 2 + (0.10 * self.reaction_time)*speed
        elif self.driving_style == 1:
            return 3 + (0.15 * self.reaction_time)*speed
        elif self.driving_style == 2:
            return 4 + (0.20 * self.reaction_time)*speed


    


for i in range(15):
    car1 = car()
    # print(car1.max_speed, car1.max_acceleration, car1.max_braking, car1.car_priority,car1.driving_style,car1.reaction_time)
    print(vars(car1))