## The Thinking Process Of The Simulator

# The thinking process behind 1 car
we store the data about 1 car such that even if we close the simulation then we can contunue from that point this means we need the following fo rthe car:
    1. Its Position (Lane No, Position along the road)
    2. Speed
    3. Direction
    4. Acceleration
    5. Driving Style - Aggressive, Calm, Nervous
    6. Destination
    7. The Route as a List of Roads
        for example if the car has to go to D then we store a list [A,B,C,D] which will store that the car goes from A to B to C and the to D, basically we make a vector triangle
    8. Routing Preference
        this will be used by the path finding algorithmm, it will be used to see if the driver prioritises the fuel or the time or etc.
    9. Car Priority
        is it a normal vehicle or an emergency vehicle
    10. Reaction time of the driver
    11. max acceleration
    12. max braking
    13. max speed

in order for the program to know that the road segment has ended it needs the data on the road too so that once the lenght of the road ends the car can shift onto the next segment

# The thinking process of the road
Every road in the simulation store the data about itself which can be accessed by what ever car is travelling on that segment, the data needed is:
    1. Lenght of the road
    2. Speed limit
    3. Number of lanes
    

# Breakdown of the road network
Nodes => intersections
Edges => roads that connect them
Cars => agents that move along the edges
Route => the sequence of nodes or edges

# The thinking process of the nodes
Every node stores the folloing information about itself
    1. Position on map
    2. type of intersection
    3. the connected road segments

# Route making algo
it does not know in what terms the route needs to be effecient so all it is given i whether to consider the lenght of the route or the time of the route
for the time it uses distance/speed formula

# Simulation Data
the data about the current simulation will then be stored for th esession which will be used to make the traffic interactive:
    1. Current time
    2. total cars
    3. comleted trips
    4. total accidents

# Simulation Road Data
this will store the data about the road under current conditions such as:
     1. numbe rof roads on the car
     2. average speed
     3. congestion level
     4. queue lenght


for each time frame the program will do the followinng:
    1. traffic condition
    2. update car info - such as new need, route changing etc
    3. recalculate the road conditons
    4. record the simulations stats
    5. render the update

the order of simulation can varies


# Simulation Model
    1. uses reaction time fo the driver to see if a collisision occurs or if he car slows down
        if the car in front slows down in front then the car behind slows and ten htere is a loop until the effect is minimized

    2. the cars will follow a simple model where they try to maintain a random distance with the car  infront, if the car is further apart they accelerate

    3. each road segment has a 2D array ehich stores the cars in rows and the lanes in columns, at each timestamp the car would access the car element in front of it ie the array element before it, then it access its data to find its speed, distance acc etc to ensure if the current car can contine on the current if not then it accelerates or decelerates as per need,
    same logic with lane changes, it is removed from the column then added to the other by first checking where it fits in the postions
    now at an intersection the car is removed from this array and then added to the array of the next segment

    4. the nodes atore the data on traffic light too and once the car is enough close it starts to consoder it, if green no effect, if red calculates the deceleration based on speed etc
    the closeness will be calculated by maths by considering speed etc
    the cars calcukated eta will be compared to the tiem remaining of the traffic light and then decidion is made
    every calculation is made for every timestamp

    5. incase of conflicitng lane changes 2 possibiltes:
        1. both attempt, calculate if not safe they wait or slowdown, try again at next timestamp
        2. both try to merge, if distance smaller then collision threshold then collision occurs

        to allow for merging to happen a priority rule that the car on the rigth gets to merge

    6. mergeing into the main road:
        a function calculates the gap between the 2 cars on the main road and then the car merging checks if that gap is big enough, if yes it merges else it waits

# Order of Update
1. Update traffic lights  
2. Cars observe environment
3. Cars make decisions - accelerate, brake, change lane
4. Cars physically move
5. Handle transitions - lane changes, road changes, completed trips
6. Update traffic metrics

# Physics
to find out the acceleration the car will need to calculate it using th eformula vf2​=vi2​+2aΔx - will do it every timeframe

every car wwill ave a maximum acceleration which will vary for each, if the calculated acc is more then that it will only accelerate till its max

the driving style now comes into play, if the driver is aggressive he uses the max acceleration evertime when possible but if the drievr is calm he uses 40 to 70% of the required acceleration

for each acceleration the car has a target acceleration, and it reaches there gradually, everytime there are no changes in observation the car increases its acceleration y 10% of the remaining gap until it reaches the target    anew​=acurrent​+0.10(atarget​−acurrent​)

the observation remains same refers to the change in gap due to the car in front, if the change in gap is more then 10% then the driver react. could also be th eproperty of the driver

so if the difference requires the reaction then the same working is done to calculate the new tagret acc


descision making flowchart
        CAR OBSERVES
            ↓
        1. Calculate gap
            ↓
        2. Check traffic light
            ↓
        Does the light affect this car?
            │
            ├── NO ───────────────┐
            │                     ↓
            │              Ignore light
            │                     │
            └── YES               │
                ↓                 │
        Calculate required        │
        behaviour for light       │
                │                 │
                └────────┬───────┘
                        ↓
        3. Calculate relative speed
        with car ahead
                        ↓
        4. Calculate target acceleration
        based on gap + relative speed
                        ↓
        5. If traffic light affects car:
                        ↓
            Is calculated acceleration
            sufficient to obey the light?
                    │             │
                    YES            NO
                    │             │
                    │       Reduce target
                    │       acceleration
                    └──────┬──────┘
                            ↓
                Set target acceleration
                            ↓
                Gradually approach target

Whenever multiple acceleration calculations are relevant, the car follows the smallest acceleration.

we use the same logic of accelrlation for raking, and if the braking is impossible a collision occurs


# Lane Changing/Overtaking
we use the principles of merging here

        Car wants to change lane
                    ↓
            Check target lane
                    ↓
            Find nearest car ahead
            Find nearest car behind
                    ↓
            Calculate gaps
                    ↓
            Are both gaps safe?
            │              │
            YES             NO
            ↓               ↓
            Change lane       Wait

for any routing preference the car wil be more aggressive and will try to fit in smaller gaps and force others to slow down

# Intersections

Current road
    ↓
Car reaches end
    ↓
Check route
    ↓
Find next road
    ↓
Enter intersection
    ↓
Continue into next road
    ↓
Use normal lane/car-following logic

# Intersection Conflict
Cars approach intersection
        ↓
Conflict detected
        ↓
Assign priorities
        ↓
Highest priority gets access
        ↓
Other car waits
        ↓
Conflict resolves


# Destination Selection
- Array of all possible destinations
- a random index of the array generated then that is the destination
- for spawing th esame function as destination occurs and once the car reaches destination it despawns for every car that despawns a new one spawns
- each road has a spawn probabilty based on its location

NEW CAR
   │
   ├── weighted random → starting point
   │
   ├── random → destination
   │
   ├── random → car type
   │
   ├── random → driving style
   │
   ├── random → routing preference
   │
   └── Dijkstra → route

# Routing Algorithm
for distance = road length
for time => roadlenght/estimates speed

CONGESTION DETECTED
        ↓
Has it lasted > 10 timestamps?
        ↓
       YES
        ↓
Has the car travelled only ~10%
of its total route during that congestion?
        ↓
       YES
        ↓
Recalculate route with Dijkstra


# Simulation Metrics
1. Average speed
2. Choke points
3. Maximum car density



## Task TODO

1. Project Setup
    <!-- Set up Python project -->
    <!-- Install libraries -->
    <!-- Create project structure -->
    Create main simulation loop
    <!-- Define simulation timestep -->
2. Core Data Structures
    <!-- Design Car -->
    <!-- Design Road -->
    <!-- Design Node -->
    Design TrafficLight
    Design Simulation
    Design road network structure
    Define relationships between objects
3. Road Network
    Create nodes/intersections
    Create roads
    <!-- Add road properties -->
    Connect roads to nodes
    <!-- Implement lane structure -->
    Build/test sample road network
4. Car System
    <!-- Implement car properties -->
    <!-- Implement driver properties -->
    <!-- Implement vehicle properties -->
    Implement route/destination data
    Implement car priority
<!-- 5. Basic Car Physics -->
    <!-- Implement acceleration -->
    <!-- Implement braking -->
    <!-- Implement speed updates -->
    <!-- Implement position updates -->
    <!-- Implement speed limits -->
    <!-- Implement vehicle limits -->
6. Car Following
    <!-- Detect car ahead -->
    <!-- Calculate gap -->
    <!-- Calculate relative speed -->
    <!-- Calculate required acceleration -->
    Implement reaction time
    <!-- Implement safe following distance -->
    Implement collision prevention
7. Driver Behaviour
    <!-- Implement aggressive drivers -->
    <!-- Implement calm drivers -->
    <!-- Implement nervous drivers -->
    <!-- Implement driver-specific acceleration -->
    <!-- Implement driver-specific gap acceptance -->
8. Traffic Lights
    Create traffic-light system
    Implement light cycles
    Implement traffic-light detection
    Calculate stopping/acceleration requirements
    Integrate lights with car behaviour
9. Road Transitions
    Detect road endings
    Determine next road
    Move cars between roads
    Preserve/update lane
    Detect destination arrival
10. Pathfinding & Routing
    Implement graph representation
    Implement Dijkstra
    Implement distance-based routing
    Implement time-based routing
    Implement routing preferences
    Implement route tracking
11. Lane Changing
    Detect when lane change is needed
    Select target lane
    Check surrounding cars
    Calculate safe gaps
    Execute lane change
    Implement overtaking
    Handle simultaneous lane changes
12. Merging
    Detect merge situations
    Find gaps
    Calculate safe merge distance
    Implement merge behaviour
    Handle conflicting merges
13. Intersection Management
    Detect intersection conflicts
    Implement priority system
    Implement emergency vehicle priority
    Control intersection access
    Handle intersection collisions
14. Spawning & Despawning
    Create spawn points
    Implement weighted spawning
    Generate random car properties
    Generate destinations
    Spawn replacement cars
    Despawn completed cars
    Implement safe spawning
15. Congestion System
    Calculate road density
    Calculate average road speed
    Calculate congestion
    Calculate queue length
    Track congestion duration
    Identify bottlenecks
16. Dynamic Rerouting
    Detect persistent congestion
    Determine affected cars
    Recalculate route
    Update route during simulation
    Test route redistribution
17. Emergency Vehicles
    Implement emergency vehicle type
    Implement emergency priority
    Implement emergency routing
    Integrate with intersections/merging/lane changes
18. Simulation Engine
    Implement update order
    Implement observation phase
    Implement decision phase
    Implement movement phase
    Implement transition phase
    Implement statistics update
    Handle system conflicts
19. Analytics
    Track average speed
    Track completed trips
    Track accidents
    Track road density
    Track congestion
    Track queues
    Track bottlenecks
    Generate graphs
20. Visualization
    <!-- Render roads -->
    <!-- Render lanes -->
    Render intersections
    Render cars
    Render traffic lights
    Implement camera
    Implement zoom/pan
    Implement simulation controls
    Display statistics
    Display congestion/bottlenecks
21. Save & Load
    Design save format
    Save simulation state
    Save cars/routes
    Save traffic lights
    Save statistics
    Load simulation
    Resume simulation
22. Testing
    Test car physics
    Test car following
    Test traffic lights
    Test road transitions
    Test routing
    Test lane changing
    Test merging
    Test intersections
    Test spawning
    Test congestion
    Test emergency vehicles
    Test save/load
23. Optimization
    Profile simulation
    Optimize car detection
    Optimize pathfinding
    Optimize rendering
    Test large numbers of cars
    Fix performance bottlenecks
24. Final Polish
    Add simulation scenarios
    Add configuration options
    Improve UI
    Add debug tools
    Improve visualization
    Fix edge cases
    Final integration testing
    Documentation



## Libraries Needed
1. Pygame - visulatization
2. Numpy - arrays and managing simulation data
3. matplotlib - analytical graps
4. Networkx - for pathfinding
5. Pandas - for working on results


