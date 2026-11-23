import random
import math
from collections import deque
from dataclasses import dataclass  #used to make record datatype
from Object_Classes.turn import turn_kind, entry_lane

@dataclass(frozen=True) #frozen makes it read only
class DriverProfile:
    a: float    #max comfortable acc
    b: float    #comfortable braking
    T: float    #desired time headway
    s0: float   #minimum bumper gap
    speed_factor: float     #multiper on speed limit
    reaction: float
    #========LANE CHANGING
    politeness: float
    lane_gain: float
    lane_cooldown: float
    safe_brake: float
    turn_zone: float
    turn_weight: float
    #=========JUNCTIONS
    t_crit: float
    t_follow: float
    yield_patience: float
    box_margin: float
    box_patience: float
    yellow_decel: float
    a_lat: float

PROFILES = {
     #aggressive
    0: dict(a=3.0, b=3.0, T=1.0, s0=1.5, speed_factor=1.10, reaction=0.45,
                     #LANE CHANGE
                     politeness=0.1, lane_gain=0.15, lane_cooldown=3.0, safe_brake=5.0, turn_zone=100.0, turn_weight=2.0,
                     #JUNCTIONS
                     t_crit=2.5, t_follow=0.8, yield_patience=8.0, box_margin=0.5, box_patience=6.0, yellow_decel=2.0, a_lat=3.0), 
    #calm
    1: dict(a=2.0, b=2.0, T=1.5, s0=2.0, speed_factor=1.00, reaction=0.72,
                     #LANE CHANGE
                     politeness=0.3, lane_gain=0.30, lane_cooldown=5.0, safe_brake=4.0, turn_zone=150.0, turn_weight=3.0,
                     #JUNCTIONS
                     t_crit=3.5, t_follow=1.5, yield_patience=15.0, box_margin=2.0, box_patience=12.0, yellow_decel=3.0, a_lat=2.0),    
    #nervous
    2: dict(a=1.8, b=2.5, T=2.0, s0=3.0, speed_factor=0.92,  reaction=0.99,
                     #LANE CHANGE
                     politeness=0.5, lane_gain=0.60, lane_cooldown=8.0, safe_brake=3.0, turn_zone=220.0, turn_weight=4.0,
                     #JUNCTIONS
                     t_crit=4.5, t_follow=2.2, yield_patience=25.0, box_margin=3.5, box_patience=20.0, yellow_decel=3.5, a_lat=1.5)   
}

SPREAD ={'speed_factor':0.05, 'reaction':0.30, 'politeness':0.50, 'lane_gain':0.30, 'turn_zone':0.25}
DEFAULT_SPREAD = 0.15

def make_profiles(style, rng):
    base_stats = PROFILES[style]
    driver_stats = {}
    for stat_name, base_value in base_stats.items():
        spread = SPREAD.get(stat_name, DEFAULT_SPREAD)
        random_multiplier = rng.uniform(1.0 - spread, 1.0 + spread)
        driver_stats[stat_name] = base_value * random_multiplier
    return DriverProfile(**driver_stats)

class Car:
    def __init__(self, car_id, length, route, max_brake=8.0, rng=None,
                 lane=0, start_x=0.0, start_speed_kmh=0.0,
                 dest_road=None, dest_x=None):
            
        self.id = car_id
        self.length = length #m
        self.rng = rng or random.Random()   #this creates a random seed, generates the randomness

        #fixed properties
        self.style = self.rng.randint(0, 2)
        self.max_speed = (self.rng.choice([120, 130, 140, 150, 160, 170, 180])) / 3.6 #m/s
        self.max_brake = max_brake 

        #trip
        self.route = route      #list of all the road ids
        self.route_index = 0
        self.dest_road = dest_road      #end road
        self.dest_x = dest_x        #end road location

        #current state
        self.x = start_x    #front bumber distance from start of road
        self.v = start_speed_kmh / 3.6
        self.a = 0.0
        self.lane = lane
        self.next_turn = None

        self.finished = False

        self.profile = make_profiles(self.style, self.rng)
        self.reaction_time = self.profile.reaction

        self.history = deque()
        #self.history appends the current observation, the head is the newest observation that is atleast reaction_time old
        #Lane Changing
        self.lane_cooldown = 0.0
        self.politeness = self.profile.politeness

        self.yield_wait = 0.0   #seconds spent stopped at a giveway line
        self.box_wait = 0.0     #time spent waiting because the next road is stopped

    # -------------- HELPERS --------------
    @property #this allows us to make get the value without using a varibale
    def speed_kmh(self):
        return self.v * 3.6     #for display

    @property
    def road_id(self):
        return self.route[self.route_index]

    def desired_speed(self, limit_Kmh):
        return min(self.max_speed, limit_Kmh/3.6 * self.profile.speed_factor)

    @property
    def next_road_id(self):
        if self.route_index + 1 < (len(self.route)):
            return self.route[self.route_index +1]
        return None

    # -------------- PHYSICS --------------
    def IDM_acceleration(self, v0, gap=None, leader_v=0.0):
        '''
        v0 = desired speed
        gap = bumper to bumper distance btw leader, None if no leader
        leader_v = leader`s speed, ignored when gap is None
        '''
        Car_Profile = self.profile
        free_term = 1 - (self.v / v0) ** 4      
        """
        scaling multiplier for the vehicles max acceleration
        if self.v = 0 then it give 1, so the multiplier is 1 ie 100%
        if self.v = v0 then it gives 0, so multiplier is 0, and v is maintained
        if self.v > v0 then it gives a negative value, the vehicle decelearates
        exponent 4, for a smooth transition
        """

        if gap is None: #open road, sets speed based on desired speed
            return Car_Profile.a * free_term

        dv = self.v - leader_v
        s_star = (Car_Profile.s0 + self.v * Car_Profile.T + 
                  (self.v * dv) / (2 * math.sqrt(Car_Profile.a * Car_Profile.b)))
        '''
        s_star = desired gap the driver wants to keep
        s0 = minimum gap to be maintained always
        self.v * Car_Profile.T = distance covered in T sec, time based buffer
        self.v * dv = dynamic interaction term
        if vehicle ahead is slower, dv is +ve so this term increases the desired gap to prepare for braking
        (self.v * dv) / (2 * math.sqrt(Car_Profile.a * Car_Profile.b)) = calculates the extra space needed if a slower car is being approached 
        2 * math.sqrt(Car_Profile.a * Car_Profile.b) = scales it for gentle braking and acc
        '''
        s_star = max(s_star, Car_Profile.s0)       #to ensure its never less then minimum gap
        gap = max(gap, 0.1)     #to avoid division by 0, if cars touch   

        return Car_Profile.a * (free_term - (s_star / gap) ** 2)
        '''
        the comfortable acc of the driver
        from the free road acc the interaction term is subtracted to get the resulting acc
        square to mimic the human scaling
        '''

    def compute_acceleration(self, limit_kmh, gap=None, leader_v=0.0):
        #this function only decides but doesnt change anything
        v0 = self.desired_speed(limit_kmh)
        a = self.IDM_acceleration(v0, gap, leader_v)
        a = max(-self.max_brake, a)     #apply braking limit
        return a

    def apply(self, a, dt):
        #moves the cars
        new_v = max(0.0, self.v + a * dt)
        self.x += (self.v + new_v) / 2 * dt
        self.a = (new_v - self.v) / dt
        self.v = new_v

    def step(self, dt, limit_kmh, gap=None, leader_v=0.0):
        self.apply(self.compute_acceleration(limit_kmh, gap, leader_v), dt)

    def refresh_turn(self, roads):
        nextID = self.next_road_id
        self.next_turn = None if nextID is None else turn_kind(roads[self.road_id], roads[nextID])

    def update_route(self, roads):
        #roads is ActiveRoadList
        #either completes the trip or gets onto the next road

        #if reached the destination
        if (self.road_id == self.dest_road 
                and self.dest_x is not None
                    and self.x >= self.dest_x):
            self.finished = True
            return

        while self.x >= roads[self.road_id].lenght:
            self.x -= roads[self.road_id].lenght
            if self.route_index + 1 >= len(self.route):
                self.finished = True
                return
            turn = self.next_turn
            self.route_index += 1
            self.history.clear() #clears the observations for the car for the previous road
            self.lane = entry_lane(turn, self.lane, int(roads[self.road_id].lanes))
            self.refresh_turn(roads)

    def observe(self, t, gap, leader_v):
        self.history.append((t, gap, leader_v))
        cutoff = t - self.reaction_time

        while len(self.history) > 1 and self.history[1][0] <= cutoff:
            self.history.popleft()

    def perceived(self):
        #reaction of driver based on observation from reaction time
        _, gap, leader_v = self.history[0]
        return gap, leader_v




######## Test Block ########
if __name__ == "__main__":
    rng = random.Random(2)
    car = Car("c1", length=4.5, route=["R1"])
    car.v = 50 / 3.6

    LIMIT = 50          # km/h
    DT = 0.1
    leader_x, leader_len, leader_v = 200.0, 4.5, 0.0
    
    for i in range(1, 401):
        gap = (leader_x - leader_len) - car.x
        car.step(DT, LIMIT, gap=gap, leader_v=leader_v)
        if i % 20 == 0: #every 2 sec
            print(f"style={car.style} t={i*DT:4.1f}s  v={car.speed_kmh:5.1f} km/h  a={car.a:5.2f}  gap={gap:6.1f} m")