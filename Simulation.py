from Active_Lists.ActiveList import ActiveRoadsList, ActiveCarsNow

# CONSTANTS
SCALE_PER_M = 5
LANE_WIDTH = 3.6 #in meters
DASHES_WIDTH = 0.15 #in meters
DASH_length = 3
GAP_length = 3

DT = 0.1
#LANE CHANGING CONST.
LANE_SAFE_BRAKE = 4.0   #max braking to impose on new follower
LANE_GAIN = 0.3     #minimum benefit to change lane
LANE_COOLDOWN = 5.0



DEFAULT_LIMITS = {   # km/h, by OSM 'highway' tag
    'motorway': 100, 'trunk': 80, 'primary': 60,
    'secondary': 50, 'tertiary': 40, 'residential': 30,
}




def SortInLanes(ActiveCarsNow):
    #clears all the lanes
    for roadOBJ in ActiveRoadsList.values():
        roadOBJ.cars_data = [[] for _ in range(roadOBJ.lanes)]

    #adds all the cars into their own road and lane
    for car in ActiveCarsNow:
        ActiveRoadsList[car.road_id].cars_data[car.lane].append(car)

    for road in ActiveRoadsList.values():
        for lane in road.cars_data:
            lane.sort(key=lambda c: c.x, reverse=True)
            #reverse so that index 0 is the car furthest away

def FindLeader(car, lane, i, road):
    #same road same lane
    if i > 0:
        lead = lane[i - 1]
        gap = (lead.x - lead.length) - car.x
        return gap, lead.v

    #next road of the route
    next_id = car.next_road_id
    if next_id is None:
        return None, 0.0

    next_Road = ActiveRoadsList[next_id]
    next_Lane = min(car.lane, int(next_Road.lanes) - 1)
    cars_There = next_Road.cars_data[next_Lane]
    if not cars_There:
        return None, 0.0

    lead = cars_There[-1]
    gap = (road.lenght - car.x) + (lead.x - lead.length)
    return gap, lead.v
    
def gap_between(rear, front):
    return ((front.x - front.length) - rear.x)

def neighbours_in_lane(lane_list, x):
    leader = follower = None
    for other in lane_list:
        if other.x > x:
            leader = other  #updates to the closest car ahead
        else:
            follower = other    #first car behind the car
            break
    return leader, follower

def try_lane_change(car, road):
    lanes = road.cars_data
    limit = road.speed_limit
    current_lane = lanes[car.lane]
    i = current_lane.index(car) #index of car in the current lane

    if i > 0:
        gap = gap_between(car, current_lane[i-1])
        leader_v = current_lane[i-1].v
    else:
        gap, leader_v = None, 0.0

    a_now = car.compute_acceleration(limit, gap, leader_v)

    best_target = None
    best_score = LANE_GAIN
    for target in (car.lane-1, car.lane+1): #iterates through the neighbouring lanes
        if target < 0 or target >= len(lanes):  #checks if the lanes exit
            continue
        leader, follower = neighbours_in_lane(lanes[target], car.x)

        if leader:
            gap2, leader_v2 = gap_between(car, leader), leader.v
            if gap2 < car.profile.s0:   #if gap is less then minimum bumper gap fir th edriver
                continue
        else:
            gap2 , leader_v2 = None, 0.0

        a_new = car.compute_acceleration(limit, gap2, leader_v2)

        loss = 0.0
        if follower:
            gap_follower = gap_between(follower, car)
            if gap_follower < follower.profile.s0:
                continue
            if leader:
                a_follower_before = follower.compute_acceleration(limit, gap_between(follower, leader), leader_v)
            else:
                a_follower_before = follower.compute_acceleration(limit)
            a_follower_after = follower.compute_acceleration(limit, gap_follower, car.v)
            if a_follower_after < -LANE_SAFE_BRAKE:
                continue
            loss = max(0.0, a_follower_before - a_follower_after)
        score = (a_new - a_now) - car.politeness * loss
        if score > best_score:
            best_target, best_score = target, score

    if best_target is not None:
        current_lane.remove(car)
        target_lane = lanes[best_target]
        index = sum(1 for o in target_lane if o.x > car.x)
        target_lane.insert(index, car)
        car.lane = best_target
        car.lane_cooldown = LANE_COOLDOWN

def simulation_step(cars, dt, t):
    # t = current simulation time in sec
    SortInLanes(ActiveCarsNow)

    for car in cars:
        car.lane_cooldown = max(0.0, car.lane_cooldown - dt)

    for road in ActiveRoadsList.values():
        if len(road.cars_data) < 2:
            continue
        movers = [c for lane in road.cars_data for c in lane] #makes a list of all the cars
        for c in movers:
            if c.lane_cooldown == 0.0:
                try_lane_change(c, road)
    #deciding phase
    decisions = []
    for road in ActiveRoadsList.values():
        for lane in road.cars_data:
            for i, carOBJ in enumerate(lane):
                gap , leader_v = FindLeader(carOBJ, lane, i, road)
                car.observe(t, gap, leader_v)
                per_gap, per_leader_v = car.perceived()
                if gap is not None and gap < car.profile.s0:
                    per_gap, per_leader_v = gap, leader_v
                decisions.append((carOBJ, carOBJ.compute_acceleration(road.speed_limit, per_gap, per_leader_v)))

    for car, a in decisions:
        car.apply(a, dt)
        car.update_route(ActiveRoadsList)

    cars[:] = [c for c in cars if not c.finished] #removes any cars that is finished
