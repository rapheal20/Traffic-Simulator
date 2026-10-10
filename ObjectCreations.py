from Object_Classes.roads import roads
from Object_Classes.car import car

from Active_Lists.ActiveCars import ActiveCarsNow
from Active_Lists.ActiveRoads import ActiveRoadsList




# Road IDs, (x, y), length, lanes, orientation
# Horizontal roads: length = 60 m, width = 3 lanes
road1 = roads("AA01", (0, 0), 100, 3, 0, 60, True, [0, 250, 500], None)
road2 = roads("AA02", (0, 71.6), 100, 3, 0, 60, True, [0, 250, 500], None)
road3 = roads("AA03", (0, 143.2), 100, 3, 0, 60, True, [0, 250, 500], None)

# Vertical roads: length = 60 m, width = 2 lanes
road4 = roads("BB01", (25, 11.6), 60, 2, 1, 60, True, [0, 250, 500], None)
road5 = roads("BB02", (50, 83.2), 60, 2, 1, 60, True, [0, 250, 500], None)
road6 = roads("BB03", (100, 0), 154.8, 3, 1, 60, True, [0, 250, 500], None)


# ROAD AA01 — 3 lanes
# ROAD AA01 — 100 m, 3 lanes
car1  = car("A01", "AA01", 8,  0, 45, 0)
car2  = car("A02", "AA01", 20, 0, 30, 0)
car3  = car("A03", "AA01", 55, 1, 60, 0)
car4  = car("A04", "AA01", 80, 2, 25, 0)

# ROAD AA02 — 100 m, 3 lanes
car5  = car("A05", "AA02", 12, 0, 35, 0)
car6  = car("A06", "AA02", 28, 0, 50, 0)
car7  = car("A07", "AA02", 62, 1, 40, 0)
car8  = car("A08", "AA02", 88, 2, 25, 0)

# ROAD AA03 — 100 m, 3 lanes
car9  = car("A09", "AA03", 15, 0, 40, 0)
car10 = car("A10", "AA03", 35, 1, 60, 0)
car11 = car("A11", "AA03", 70, 1, 30, 0)
car12 = car("A12", "AA03", 92, 2, 45, 0)

# ROAD BB01 — 60 m, 2 lanes
car13 = car("B01", "BB01", 5,  0, 50, 0)
car14 = car("B02", "BB01", 25, 1, 30, 0)
car15 = car("B03", "BB01", 45, 0, 40, 0)

# ROAD BB02 — 60 m, 2 lanes
car16 = car("B04", "BB02", 10, 0, 35, 0)
car17 = car("B05", "BB02", 32, 1, 55, 0)
car18 = car("B06", "BB02", 50, 0, 25, 0)

# ROAD BB03 — 154.8 m, 3 lanes
car19 = car("B07", "BB03", 40, 1, 45, 0)
car20 = car("B08", "BB03", 110, 2, 35, 0)