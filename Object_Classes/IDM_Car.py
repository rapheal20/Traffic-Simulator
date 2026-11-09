import random
from dataclasses import dataclass  #used to make record datatype

@dataclass(frozen=True) #frozen makes it read only
class DriverProfile:
    a: float    #max comfortable acc
    b: float    #comfortable braking
    T: float    #desired time headway
    s0: float   #minimum bumper gap
    speed_factor: float     #multiper on speed limit

PROFILES = {
    0: DriverProfile(a=3.0, b=3.0, T=1.0, s0=1.5, speed_factor=1.10),    #aggressive
    1: DriverProfile(a=2.0, b=2.0, T=1.5, s0=2.0, speed_factor=1.00),    #calm
    2: DriverProfile(a=1.8, b=2.5, T=2.0, s0=3.0, speed_factor=0.92)    #nervous
}


class Car:
    def __init__(self, car_id, length, route, max_brake=8.0, rng=None):
        self.id = car_id
        self.length = length #m
        self.rng = rng or random.Random()   #this creates a random seed, generates the randomness

        #fixed properties
        self.style = self.rng.randint(0, 2)
        base = PROFILES[self.style]
        self.profile = DriverProfile(
            a= base.a * self.rng.uniform(0.85, 1.15),
            b= base.b * self.rng.uniform(0.85, 1.15),
            T= base.T * self.rng.uniform(0.85, 1.15),
            s0= base.s0 * self.rng.uniform(0.85, 1.15),
            speed_factor= base.speed_factor * self.rng.uniform(0.85, 1.15),
        ) #adds a randomness in the preset values

        self.max_speed = (self.rng.choice([120, 130, 140, 150, 160, 170, 180])) / 3.6 #m/s
        self.max_brake = max_brake 

        #trip
        self.route = route      #list of all the road ids
        self.route_index = 0

        #current state
        self.x = 0.0    #front bumber distance from start of road
        self.v = 0.0
        self.a = 0.0
        self.lane = 0

        self.finished = False

    # -------------- HELPERS --------------
    @property #this allows us to make get the value without using a varibale
    def speed_kmh(self):
        return self.v * 3.6     #for display

    @property
    def road_id(self):
        return self.route[self.route_index]

    def desired_speed(self, limit_Kmh):
        return min(self.max_speed, limit_Kmh/3.6 * self.profile.speed_factor)


    # -------------- PHYSICS --------------
    def free_acceleration(self, v0):
        return self.profile.a * (1 - (self.v / v0) ** 4)

    def step(self, dt, limit_kmh):
        v0 = self.desired_speed(limit_kmh)

        a = self.free_acceleration(v0)
        a = max(-self.max_brake, a)     #no braking harder then what physics allow

        new_v = max(0.0, self.v + a * dt)   #never reverse
        self.x += (self.v + new_v) / 2 * dt     #average speed * time
        self.a = (new_v - self.v) / dt
        self.v = (new_v)







######## Test Block ########
if __name__ == "__main__":
    rng = random.Random(2)
    car = Car("c1", length=4.5, route=["R1"])

    LIMIT = 50          # km/h
    DT = 0.1
    t = 0.0
    while t < 40:
        car.step(DT, LIMIT)
        t += DT
        if round(t, 1) % 5 == 0:
            print(f"style={car.style} t={t:4.1f}s  v={car.speed_kmh:5.1f} km/h  a={car.a:5.2f}  x={car.x:6.1f} m")